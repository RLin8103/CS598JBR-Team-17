"""Minimal OpenAI-compatible chat-completions client (standard library only).

Works with OpenRouter (default), OpenAI, vLLM, Ollama (`/v1`), LM Studio and any other
server that implements `POST {base_url}/chat/completions`.
The API key is read from an environment variable and is never written to disk.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(self, cfg: dict):
        env_over = cfg.get("env_overrides", {})
        self.base_url = os.environ.get(env_over.get("base_url", "LLM_BASE_URL"), cfg["base_url"]).rstrip("/")
        self.model = os.environ.get(env_over.get("model", "LLM_MODEL"), cfg["model"])
        key_env = os.environ.get(env_over.get("api_key_env", "LLM_API_KEY_ENV"), cfg["api_key_env"])
        self.api_key_env = key_env
        self.api_key = os.environ.get(key_env, "")
        self.temperature = cfg.get("temperature", 0.2)
        self.top_p = cfg.get("top_p", 1.0)
        self.max_tokens = cfg.get("max_tokens", 8000)
        self.timeout = cfg.get("request_timeout_s", 600)
        self.max_retries = cfg.get("max_retries", 5)
        self.backoff = cfg.get("retry_backoff_s", 10)
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.calls = 0

    def secrets(self) -> list[str]:
        """Strings that must be scrubbed from every log file."""
        return [self.api_key] if self.api_key else []

    def describe(self) -> dict:
        return {
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }

    def chat(self, messages: list[dict]) -> dict:
        """Returns {"content": str, "usage": {...}, "finish_reason": str, "seconds": float}."""
        if not self.api_key and "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
            raise LLMError(
                f"No API key found. Export {self.api_key_env} (see MP4/README.md) before running the pipeline."
            )
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
        data = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        last_err: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            started = time.time()
            try:
                req = urllib.request.Request(f"{self.base_url}/chat/completions", data=data, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                if "error" in payload and "choices" not in payload:
                    raise LLMError(f"API error: {payload['error']}")
                choice = payload["choices"][0]
                content = (choice.get("message") or {}).get("content") or ""
                if not content.strip():
                    raise LLMError("empty completion")
                usage = payload.get("usage") or {}
                self.total_prompt_tokens += int(usage.get("prompt_tokens", 0))
                self.total_completion_tokens += int(usage.get("completion_tokens", 0))
                self.calls += 1
                return {
                    "content": content,
                    "usage": usage,
                    "finish_reason": choice.get("finish_reason"),
                    "seconds": round(time.time() - started, 2),
                }
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "replace")[:500]
                last_err = LLMError(f"HTTP {exc.code}: {detail}")
                if exc.code in (400, 401, 403, 404):
                    raise last_err
            except (urllib.error.URLError, TimeoutError, LLMError, json.JSONDecodeError, KeyError) as exc:
                last_err = exc
            wait = self.backoff * attempt
            print(f"[llm] attempt {attempt}/{self.max_retries} failed ({last_err}); retrying in {wait}s", flush=True)
            time.sleep(wait)
        raise LLMError(f"LLM request failed after {self.max_retries} attempts: {last_err}")

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens
