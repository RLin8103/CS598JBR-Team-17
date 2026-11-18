"""Minimal OpenAI-compatible chat-completions client (standard library only).

Works with OpenRouter (default), OpenAI, vLLM, Ollama (`/v1`), LM Studio and any other
server that implements `POST {base_url}/chat/completions`.
The API key is read from an environment variable and is never written to disk.

Free endpoints are flaky, so the client can fall back to other models
(`fallback_models` in configs/pipeline.json, or env LLM_FALLBACK_MODELS=a,b,c) and
reports *why* a reply was unusable (finish reason, token usage, reasoning-only output).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

from budget import Budget, BudgetError
import urllib.error
import urllib.request


class LLMError(RuntimeError):
    pass


class FatalModelError(LLMError):
    """The current model cannot serve requests (bad id, no access): try the next model."""


class LLMClient:
    def __init__(self, cfg: dict):
        env_over = cfg.get("env_overrides", {})
        self.base_url = os.environ.get(env_over.get("base_url", "LLM_BASE_URL"), cfg["base_url"]).rstrip("/")
        self.model = os.environ.get(env_over.get("model", "LLM_MODEL"), cfg["model"])
        fb_env = os.environ.get("LLM_FALLBACK_MODELS")
        fallbacks = [m.strip() for m in fb_env.split(",") if m.strip()] if fb_env else list(cfg.get("fallback_models", []))
        self.fallbacks = [m for m in fallbacks if m != self.model]
        key_env = os.environ.get(env_over.get("api_key_env", "LLM_API_KEY_ENV"), cfg["api_key_env"])
        self.api_key_env = key_env
        self.api_key = os.environ.get(key_env, "")
        self.temperature = cfg.get("temperature", 0.2)
        self.top_p = cfg.get("top_p", 1.0)
        self.max_tokens = cfg.get("max_tokens", 8000)
        self.extra_body = cfg.get("extra_body") or {}
        self.api_style = cfg.get("api_style", "openai")
        self.local_options = cfg.get("local_options", {})
        self.timeout = cfg.get("request_timeout_s", 600)
        self.max_retries = cfg.get("max_retries", 5)
        self.backoff = cfg.get("retry_backoff_s", 10)
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.calls = 0
        self.attempted_calls = 0
        self.api_responses = 0
        self.reported_cost_usd = 0.0
        self.on_event = lambda *args, **kwargs: None
        self.budget = None
        self.budget_limit = cfg.get("budget_usd") if cfg.get("budget_usd") is not None else os.environ.get("CRUST_BUDGET_USD")
        self.max_calls = cfg.get("max_api_calls", 1000)
        self.budget_ledger = cfg.get("budget_ledger", "evaluation/spending.json")
        self.access_catalogue = cfg.get("access_catalogue", "evaluation/access_verified.json")
        self.model_switches: list[dict] = []

    def secrets(self) -> list[str]:
        """Strings that must be scrubbed from every log file."""
        return [self.api_key] if self.api_key else []

    def describe(self) -> dict:
        return {
            "base_url": self.base_url,
            "model": self.model,
            "fallback_models": self.fallbacks,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "extra_body": self.extra_body,
            "api_style": self.api_style, "local_options": self.local_options,
            "budget_usd": self.budget_limit,
            "budget_ledger": self.budget_ledger,
            "access_catalogue": self.access_catalogue,
            "max_api_calls": self.max_calls,
        }

    # ------------------------------------------------------------------ single model
    def _request(self, model: str, messages: list[dict]) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key and self.api_style != "ollama":
            headers["Authorization"] = f"Bearer {self.api_key}"
        last_err: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            started = time.time()
            if self.attempted_calls >= self.max_calls:
                raise LLMError(f"budget_blocked: maximum API calls ({self.max_calls}) reached")
            if any(k in self.extra_body for k in ("model", "messages", "max_tokens", "max_completion_tokens", "tools", "plugins", "provider")):
                raise LLMError("extra_body cannot override model, messages, token limit, routing, or enable paid tools/plugins")
            body = {
                "model": model,
                "messages": messages,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens,
                **self.extra_body,
            }
            if self.budget is not None:
                try:
                    body["provider"] = self.budget.reserve(model, self.max_tokens)
                except BudgetError as exc:
                    raise LLMError(f"budget_blocked: {exc}") from exc
                supported = self.budget.catalogue["models"][model].get("supported_parameters") or []
                for param in ("temperature", "top_p"):
                    if param not in supported:
                        body.pop(param, None)
            endpoint = f"{self.base_url}/chat/completions"
            if self.api_style == "ollama":
                if urlparse(self.base_url).hostname not in ("localhost", "127.0.0.1", "::1"):
                    raise LLMError("Native Ollama adapter is restricted to an explicitly configured local host")
                endpoint = f"{self.base_url}/api/chat"
                body = {"model": model, "messages": messages, "stream": False,
                        "options": {**self.local_options, "num_predict": self.max_tokens,
                                    "temperature": self.temperature, "top_p": self.top_p}}
                if isinstance(self.extra_body.get("think"), bool):
                    body["think"] = self.extra_body["think"]
            data = json.dumps(body).encode("utf-8")
            try:
                req = urllib.request.Request(endpoint, data=data, headers=headers)
                self.attempted_calls += 1
                self.on_event("api_attempt", model=model, attempt=attempt, api_calls_attempted=self.attempted_calls)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    self.api_responses += 1
                    payload = json.loads(resp.read().decode("utf-8"))
                if self.api_style == "ollama":
                    if payload.get("done") is not True or not isinstance(payload.get("message"), dict):
                        raise LLMError("incomplete/malformed native Ollama response")
                    payload = {"choices": [{"message": payload["message"], "finish_reason": payload.get("done_reason")}],
                               "usage": {"prompt_tokens": payload.get("prompt_eval_count", 0),
                                         "completion_tokens": payload.get("eval_count", 0), "cost": 0.0}}
                if "error" in payload and "choices" not in payload:
                    raise LLMError(f"API error: {str(payload['error'])[:300]}")
                choice = payload["choices"][0]
                message = choice.get("message") or {}
                content = message.get("content") or ""
                usage = payload.get("usage") or {}
                self.total_prompt_tokens += int(usage.get("prompt_tokens", 0))
                self.total_completion_tokens += int(usage.get("completion_tokens", 0))
                if isinstance(usage.get("cost"), (float, int)):
                    self.reported_cost_usd += usage["cost"]
                self.on_event("api_response", model=model, usage=usage, content_present=bool(content.strip()),
                              finish_reason=choice.get("finish_reason"))
                if not content.strip():
                    reasoning = message.get("reasoning") or ""
                    details = usage.get("completion_tokens_details") or {}
                    raise LLMError(
                        f"empty completion (finish_reason={choice.get('finish_reason')}, "
                        f"prompt_tokens={usage.get('prompt_tokens')}, completion_tokens={usage.get('completion_tokens')}, "
                        f"reasoning_tokens={details.get('reasoning_tokens')}, reasoning_chars={len(reasoning)}, "
                        f"provider={payload.get('provider')})"
                    )
                self.calls += 1
                return {
                    "content": content,
                    "usage": usage,
                    "finish_reason": choice.get("finish_reason"),
                    "seconds": round(time.time() - started, 2),
                    "model": model,
                }
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:400]
                if self.api_key:
                    detail = detail.replace(self.api_key, "[REDACTED]")
                last_err = LLMError(f"HTTP {exc.code}: {detail}")
                if exc.code in (401, 403):
                    raise LLMError(f"authentication failed ({exc.code}); check the API key: {detail}")
                if exc.code == 400 and self.extra_body:
                    # Some providers reject optional parameters (e.g. `reasoning`): drop them and retry once.
                    print(f"[llm] {model}: HTTP 400 with extra_body {list(self.extra_body)}; retrying without it ({detail[:160]})", flush=True)
                    self.extra_body = {}
                    continue
                if exc.code in (400, 404):
                    raise FatalModelError(f"model {model} rejected the request: HTTP {exc.code}: {detail}")
            except (urllib.error.URLError, TimeoutError, LLMError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError, AttributeError) as exc:
                last_err = exc
            self.on_event("api_failure", model=model, attempt=attempt, error=str(last_err))
            if attempt == self.max_retries:
                break
            wait = min(self.backoff * attempt, 60)
            print(f"[llm] {model}: attempt {attempt}/{self.max_retries} failed ({last_err}); retrying in {wait}s", flush=True)
            time.sleep(wait)
        raise LLMError(f"{model}: failed after {self.max_retries} attempts: {last_err}")

    # ------------------------------------------------------------------ with fallbacks
    def chat(self, messages: list[dict]) -> dict:
        """Returns {"content", "usage", "finish_reason", "seconds", "model"}; switches model on failure."""
        hostname = urlparse(self.base_url).hostname
        local = hostname in ("localhost", "127.0.0.1", "::1")
        if not self.api_key and not local:
            raise LLMError(
                f"No API key found. Export {self.api_key_env} (see MP4/README.md) before running the pipeline."
            )
        if not local and self.budget is None:
            if hostname != "openrouter.ai" or urlparse(self.base_url).scheme != "https":
                raise LLMError("Remote inference requires a documented spending adapter; this controller currently supports OpenRouter HTTPS")
            if self.budget_limit is None or self.budget_limit == "":
                raise LLMError("budget_blocked: set an explicit CRUST_BUDGET_USD total; token limits are not dollar authorization")
            root = Path(__file__).resolve().parent.parent
            try:
                self.budget = Budget(self.budget_limit, root / self.budget_ledger, root / self.access_catalogue)
            except (BudgetError, OSError, ValueError, KeyError) as exc:
                raise LLMError(f"budget_blocked: {exc}") from exc
        candidates = [self.model] + [m for m in self.fallbacks if m != self.model]
        errors = []
        for model in candidates:
            try:
                resp = self._request(model, messages)
                if model != self.model:
                    self.model_switches.append({"from": self.model, "to": model, "reason": errors[-1] if errors else ""})
                    print(f"[llm] switching to fallback model {model}", flush=True)
                    self.model = model
                    self.fallbacks = [m for m in self.fallbacks if m != model]
                return resp
            except LLMError as exc:
                if "authentication failed" in str(exc) or "budget_blocked" in str(exc):
                    raise
                errors.append(str(exc))
                print(f"[llm] giving up on {model}: {exc}", flush=True)
        raise LLMError("all models failed: " + " | ".join(errors))

    def escalate(self, reason: str) -> bool:
        """Switch (sticky) to the next fallback model, e.g. when the current one keeps producing replies without edits."""
        if not self.fallbacks:
            return False
        nxt = self.fallbacks.pop(0)
        self.model_switches.append({"from": self.model, "to": nxt, "reason": reason})
        print(f"[llm] escalating to model {nxt}: {reason}", flush=True)
        self.model = nxt
        return True

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens
