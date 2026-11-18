"""Conservative shared OpenRouter request reservations; no credentials are stored."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import fcntl
import json
from pathlib import Path


class BudgetError(RuntimeError):
    pass


def amount(value):
    try:
        out = Decimal(str(value))
    except InvalidOperation as exc:
        raise BudgetError("invalid USD amount") from exc
    if not out.is_finite() or out < 0:
        raise BudgetError("USD amounts must be finite and nonnegative")
    return out


class Budget:
    def __init__(self, limit, ledger: Path, catalogue: Path):
        self.limit = amount(limit)
        self.ledger = ledger
        self.catalogue = json.loads(catalogue.read_text())
        retrieved = datetime.fromisoformat(self.catalogue["retrieved_utc"])
        age = (datetime.now(timezone.utc) - retrieved).total_seconds()
        if not 0 <= age <= 86400 or self.catalogue.get("authenticated_access_verified") is not True:
            raise BudgetError("Run preflight.py with the credential in the environment to refresh authenticated access and pricing")

    def reserve(self, model, max_tokens):
        info = self.catalogue["models"].get(model)
        if not info:
            raise BudgetError(f"model unavailable in verified catalogue: {model}; no automatic substitution authorized")
        pricing = info["pricing"]
        tiers = [pricing, *pricing.get("overrides", [])]
        prompt = max(amount(t.get("prompt", pricing["prompt"])) for t in tiers)
        completion = max(amount(t.get("completion", pricing["completion"])) for t in tiers)
        if self.limit == 0:
            if not model.endswith(":free") or prompt != 0 or completion != 0:
                raise BudgetError("zero-dollar authorization permits only verified :free models with zero token prices")
            for field in ("request", "image", "web_search", "internal_reasoning"):
                if amount(pricing.get(field, 0)) != 0:
                    raise BudgetError(f"zero-dollar authorization rejects a nonzero {field} price")
        # Full context plus maximum completion deliberately overestimates a request.
        # Failed/ambiguous requests keep their reservation; never retry for free.
        bound = Decimal(info["context_length"]) * prompt + Decimal(max_tokens) * completion
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a+", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            fh.seek(0)
            contents = fh.read()
            state = json.loads(contents) if contents else {"limit_usd": str(self.limit), "reserved_usd": "0", "requests": []}
            # Reusing a ledger never resets its spent/reserved amount between projects/runs.
            if amount(state["limit_usd"]) != self.limit:
                raise BudgetError("shared ledger budget differs; inspect it and explicitly reconcile the authorized limit")
            reserved = amount(state["reserved_usd"])
            if reserved + bound > self.limit:
                raise BudgetError(f"budget exhausted: {reserved} reserved + {bound} request bound > {self.limit} USD")
            state["reserved_usd"] = str(reserved + bound)
            state["requests"].append({"model": model, "maximum_usd": str(bound), "t": datetime.now(timezone.utc).isoformat()})
            fh.seek(0); fh.truncate(); fh.write(json.dumps(state, indent=2) + "\n"); fh.flush()
        return {"max_price": {"prompt": float(prompt * 1000000), "completion": float(completion * 1000000)},
                "require_parameters": True}
