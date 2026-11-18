import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from budget import Budget, BudgetError
from llm import LLMClient, LLMError

ROOT = Path(__file__).resolve().parents[2]


class BudgetTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.data = {"retrieved_utc":datetime.now(timezone.utc).isoformat(), "authenticated_access_verified":True,
            "models":{"fixture":{"context_length":100, "pricing":{"prompt":"0.001", "completion":"0.002"}}}}
        self.catalogue = self.root / "catalogue.json"
        self.catalogue.write_text(json.dumps(self.data))

    def test_budget_requires_explicit_finite_positive_amount(self):
        for value in (-1, "NaN", "Infinity", "not-a-number"):
            with self.subTest(value=value), self.assertRaises(BudgetError):
                Budget(value, self.root / "ledger.json", self.catalogue)

    def test_zero_budget_accepts_only_verified_free_models(self):
        self.data["models"]["fixture:free"] = {"context_length": 100, "pricing": {"prompt": "0", "completion": "0"}}
        self.catalogue.write_text(json.dumps(self.data))
        budget = Budget(0, self.root / "free-ledger", self.catalogue)
        self.assertEqual(budget.reserve("fixture:free", 10)["max_price"], {"prompt": 0.0, "completion": 0.0})
        with self.assertRaises(BudgetError): budget.reserve("fixture", 10)
        self.data["models"]["fixture:free"]["pricing"]["request"] = "0.01"
        self.catalogue.write_text(json.dumps(self.data))
        with self.assertRaises(BudgetError): Budget(0, self.root / "other-ledger", self.catalogue).reserve("fixture:free", 10)

    def test_conservative_reservation_survives_new_client_and_exhausts_total(self):
        ledger = self.root / "ledger.json"
        first = Budget("0.25", ledger, self.catalogue)
        self.assertEqual(first.reserve("fixture", 10)["max_price"], {"prompt":1000., "completion":2000.})
        second = Budget("0.25", ledger, self.catalogue)
        second.reserve("fixture", 10)
        with self.assertRaises(BudgetError):
            second.reserve("fixture", 10)
        self.assertEqual(len(json.loads(ledger.read_text())["requests"]), 2)

    def test_missing_model_and_unverified_access_are_blocked(self):
        budget = Budget(1, self.root / "ledger", self.catalogue)
        with self.assertRaises(BudgetError):
            budget.reserve("not-listed", 10)
        self.data["authenticated_access_verified"] = False
        self.catalogue.write_text(json.dumps(self.data))
        with self.assertRaises(BudgetError):
            Budget(1, self.root / "ledger", self.catalogue)

    def test_stale_catalogue_blocked(self):
        self.data["retrieved_utc"] = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        self.catalogue.write_text(json.dumps(self.data))
        with self.assertRaises(BudgetError):
            Budget(1, self.root / "ledger", self.catalogue)

    def test_remote_calls_without_budget_never_open_network(self):
        cfg = json.loads((ROOT / "configs/pipeline.json").read_text())["llm"]
        with patch.dict("os.environ", {"OPENROUTER_API_KEY":"fixture-secret"}, clear=True), patch("urllib.request.urlopen") as open_url:
            client = LLMClient(cfg)
            with self.assertRaisesRegex(LLMError, "budget_blocked"):
                client.chat([])
            open_url.assert_not_called()
            self.assertEqual(client.attempted_calls, 0)

    def test_provider_credit_mode_omits_token_cap_and_keeps_reservation_ledger(self):
        ledger = self.root / "ledger"
        ledger.write_text("historical ledger")
        cfg = json.loads((ROOT / "configs/pipeline.json").read_text())["llm"]
        cfg.update(model="fixture", fallback_models=[], access_catalogue=str(self.catalogue),
                   budget_ledger=str(ledger), budget_usd=4.90, provider_credit_limit=True, max_tokens=None)
        payload = {"choices": [{"message": {"content": "fixture"}, "finish_reason": "stop"}],
                   "usage": {"prompt_tokens": 10, "completion_tokens": 20, "cost": 0.005}}
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "fixture-secret"}, clear=True), patch("urllib.request.urlopen") as open_url:
            open_url.return_value.__enter__.return_value.read.return_value = json.dumps(payload).encode()
            client = LLMClient(cfg)
            self.assertEqual(client.chat([])["content"], "fixture")
            body = json.loads(open_url.call_args.args[0].data)
            self.assertNotIn("max_tokens", body)
            self.assertNotIn("provider", body)
            self.assertEqual(client.reported_cost_usd, 0.005)
        self.assertEqual(ledger.read_text(), "historical ledger")

    def test_localhost_substring_does_not_bypass_remote_auth(self):
        cfg = json.loads((ROOT / "configs/pipeline.json").read_text())["llm"]
        cfg["base_url"] = "https://example.com/localhost"
        with patch.dict("os.environ", {}, clear=True), patch("urllib.request.urlopen") as open_url:
            with self.assertRaisesRegex(LLMError, "No API key"):
                LLMClient(cfg).chat([])
            open_url.assert_not_called()


if __name__ == "__main__":
    unittest.main()
