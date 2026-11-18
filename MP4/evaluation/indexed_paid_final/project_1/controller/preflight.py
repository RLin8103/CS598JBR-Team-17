#!/usr/bin/env python3
"""Verify OpenRouter authentication and catalogue access using GET requests only."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlparse

from llm import LLMClient

MP4 = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=MP4 / "configs/pipeline.json")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    client = LLMClient(json.loads(args.config.read_text())["llm"])
    if urlparse(client.base_url).hostname != "openrouter.ai":
        raise SystemExit("This preflight supports OpenRouter only; use a documented adapter for other providers")
    if not client.api_key:
        raise SystemExit(f"Missing {client.api_key_env}; set it in the runtime environment without placing it in files or chat")
    def get(path):
        req = urllib.request.Request(client.base_url + path, headers={"Authorization": "Bearer " + client.api_key})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except Exception as exc:
            # Provider response bodies can echo credentials; do not print them.
            raise SystemExit(f"GET {path} failed ({type(exc).__name__}); no inference call was made") from None
    key = get("/key")
    if not isinstance(key.get("data"), dict):
        raise SystemExit("Malformed authentication response")
    catalogue = {m["id"]: m for m in get("/models")["data"]}
    ids = [client.model, *client.fallbacks]
    out = {"retrieved_utc": datetime.now(timezone.utc).isoformat(), "source": client.base_url + "/models",
           "authenticated_access_verified": True, "inference_calls": 0,
           "models": {model: {k: catalogue[model].get(k) for k in ("id", "context_length", "pricing", "supported_parameters")}
                      if model in catalogue else None for model in ids}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"authentication_verified": True, "models_present": {k: v is not None for k, v in out["models"].items()},
                      "inference_calls": 0}, indent=2))


if __name__ == "__main__":
    main()
