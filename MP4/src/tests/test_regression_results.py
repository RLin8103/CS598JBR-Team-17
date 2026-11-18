"""Exercise snapshot decisions and reject incomplete or misattributed evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import Pipeline
from regression_results import named_outcomes, run_additional_check

MP4 = Path(__file__).resolve().parents[2]


def process(stdout, returncode=0, timed_out=False):
    return dict(stdout=stdout, stderr="", returncode=returncode, timed_out=timed_out)


class RegressionResultsTests(unittest.TestCase):
    def test_failed_suite_can_supply_complete_named_results(self):
        listing = process("case_a: test\ncase_b: test\n")
        summary = "test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured;"
        text = f"test case_a ... ok\ntest case_b ... FAILED\n{summary}"
        self.assertEqual(named_outcomes(listing, process(text, 101)), {"case_a": "ok", "case_b": "FAILED"})
        for execution in [process(text, 0), process(text, 101, True), process(text.replace("test case_b ... FAILED\n", ""), 101)]:
            with self.subTest(execution=execution), self.assertRaises(ValueError):
                named_outcomes(listing, execution)

    def test_stale_malformed_and_wrong_hash_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results"
            crate = MP4 / "translations/project_1"
            runner = str(MP4 / "src/run_regressions.py")
            args = dict(output=output, project_id=1, crate=crate, mp4=MP4, python=sys.executable, env={}, timeout=1)
            output.mkdir()
            self.assertIsNone(run_additional_check(runner, **args)["outcomes"])
            output.rmdir()
            for evidence in ("{", '{"source_sha256": {"1": {"src/cset.rs": "wrong"}}}'):
                with self.subTest(evidence=evidence):
                    def mock_run(*unused):
                        output.mkdir(exist_ok=True)
                        (output / "results.json").write_text(evidence)
                        return process("", 1)

                    with patch("regression_results.run_cmd", side_effect=mock_run):
                        result = run_additional_check(runner, **args)
                    self.assertFalse(result["ok"])
                    self.assertIsNone(result["outcomes"])
                    self.assertIn("validation_error", result)
                    (output / "results.json").unlink()
                    output.rmdir()


class RepairSelectionTests(unittest.TestCase):
    def state(self, outcomes):
        return dict(policy=[], interface=[], compiles=True, passed=15, total=15, failed=0,
                    test=dict(valid_output=True, returncode=0, test_results={"benchmark": 15}),
                    clippy={"ok": True}, unsafe={"tool": "official", "valid": True},
                    additional_checks=[{"ok": False, "outcomes": outcomes}], score=(1,))

    def test_named_improvement_with_unchanged_benchmark_and_suite_status(self):
        before = self.state(dict(one="ok", two="FAILED", three="FAILED"))
        after = self.state(dict(one="ok", two="ok", three="FAILED"))
        self.assertIsNone(Pipeline.repair_rejection(after, before))

    def test_lost_or_invalid_regression_outcomes(self):
        before = self.state(dict(one="ok", two="FAILED"))
        for outcomes in (dict(one="FAILED", two="ok"), dict(two="ok"), None):
            with self.subTest(outcomes=outcomes):
                self.assertIsNotNone(Pipeline.repair_rejection(self.state(outcomes), before))

    def test_protected_and_interface_violations(self):
        before = self.state(dict(one="FAILED"))
        for violation in ("policy", "interface"):
            after = self.state(dict(one="ok"))
            after[violation] = ["change to protected API or file"]
            self.assertIsNotNone(Pipeline.repair_rejection(after, before))

    def test_replay_rejected_haiku_edit(self):
        run = MP4 / "trajectories/project_2/run_20261118_010837_713513"
        before, candidate = [json.loads((run / f"iteration_{n:02d}/validation.json").read_text()) for n in (0, 2)]
        self.assertEqual((before["passed"], candidate["passed"]), (6, 4))
        self.assertIn("benchmark", Pipeline.repair_rejection(candidate, before))
        self.assertTrue((run / "iteration_02/files/src/psbt.rs").is_file())
