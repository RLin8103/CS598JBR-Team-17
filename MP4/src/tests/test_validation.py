"""Controller regressions. These never modify or replace benchmark tests."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import Pipeline
from tools import CargoTools, Workspace, PRIMARY, run_cmd, unsafe_primary_total
import interface_check

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "configs/pipeline.json").read_text())


def execution(stdout="", returncode=0, timed_out=False, stderr=""):
    return dict(cmd="fixture", returncode=returncode, timed_out=timed_out,
                stdout=stdout, stderr=stderr, seconds=0)


PASS = "running 1 test\ntest example ... ok\ntest result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s\n"


def clean_state():
    return dict(policy=[], interface=[], stubs=[], compiles=True, passed=1, failed=0, total=1,
                build={"ok": True, "error_count": 0}, test={"ok": True, "valid_output": True},
                clippy={"ok": True}, clippy_total=0, unsafe_total=0,
                unsafe={"tool": "official", "valid": True, "totals": dict.fromkeys(PRIMARY, 0)})


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cargo = CargoTools(self.root, CFG["toolchain"], self.root / "target", copy.deepcopy(CFG))
        self.pipeline = Pipeline.__new__(Pipeline)
        self.pipeline.cfg = copy.deepcopy(CFG)

    def parse_test(self, res):
        with patch.object(self.cargo, "_cargo", return_value=res):
            return self.cargo.test()

    def test_successful_test_output(self):
        t = self.parse_test(execution(PASS))
        self.assertTrue(t["ok"])
        self.assertEqual((t["passed"], t["distinct_total"]), (1, 1))

    def test_passing_summary_followed_by_nonzero_exit(self):
        self.assertFalse(self.parse_test(execution(PASS, 101))["ok"])

    def test_passing_summary_followed_by_timeout(self):
        self.assertFalse(self.parse_test(execution(PASS, 0, True))["ok"])

    def test_incomplete_second_harness(self):
        t = self.parse_test(execution(PASS + "running 1 test\n"))
        self.assertFalse(t["valid_output"])
        self.assertFalse(t["ok"])

    def test_malformed_or_empty_output(self):
        for text in ("", "test result: ok. 1 passed; 0 failed; 0 ignored", PASS.replace("1 passed", "2 passed")):
            with self.subTest(text=text):
                self.assertFalse(self.parse_test(execution(text))["ok"])

    def test_duplicates_are_executions_not_distinct_tests(self):
        t = self.parse_test(execution(PASS + PASS))
        self.assertTrue(t["ok"])
        self.assertEqual((t["passed"], t["total"], t["distinct_passed"], t["distinct_total"]), (2, 2, 1, 1))

    def test_failed_test_is_valid_measurement_but_not_success(self):
        text = PASS.replace("... ok", "... FAILED").replace("result: ok", "result: FAILED").replace("1 passed; 0 failed", "0 passed; 1 failed")
        t = self.parse_test(execution(text, 101))
        self.assertTrue(t["valid_output"])
        self.assertFalse(t["ok"])
        self.assertEqual(t["failed"], 1)

    def test_missing_executable_records_failure(self):
        t = run_cmd([str(self.root / "not-installed")], self.root, os.environ.copy(), 1)
        self.assertIsNone(t["returncode"])
        self.assertIn("launch_error", t)

    def test_real_process_timeout_preserves_partial_output(self):
        t = run_cmd([sys.executable, "-c", "import time; print('partial', flush=True); time.sleep(10)"], self.root, os.environ.copy(), 0.1)
        self.assertTrue(t["timed_out"])
        self.assertIn("partial", t["stdout"])

    def test_official_schema_rejects_missing_negative_bool_string_and_containers(self):
        self.cargo.cfg["unsafe_metrics"]["command"] = "analyzer {path}"
        for value in ({}, [], None, 0, {**dict.fromkeys(PRIMARY, 0), "unsafe_lines": -1},
                      {**dict.fromkeys(PRIMARY, 0), "unsafe_lines": True},
                      {**dict.fromkeys(PRIMARY, 0), "unsafe_lines": "0"}):
            with self.subTest(value=value), patch("tools.run_cmd", return_value=execution(json.dumps(value))):
                t = self.cargo.unsafe_metrics()
                self.assertFalse(t["valid"])
                self.assertIsNone(unsafe_primary_total(t))

    def test_invalid_official_json_is_unknown_not_zero(self):
        self.cargo.cfg["unsafe_metrics"]["command"] = "analyzer"
        with patch("tools.run_cmd", return_value=execution("not JSON")):
            t = self.cargo.unsafe_metrics()
        self.assertIsNone(t["totals"])
        self.assertIsNone(unsafe_primary_total(t))

    def test_official_nonzero_or_timeout_is_not_valid_even_with_zero_metrics(self):
        self.cargo.cfg["unsafe_metrics"]["command"] = "analyzer"
        for rc, timeout in ((1, False), (0, True)):
            with patch("tools.run_cmd", return_value=execution(json.dumps(dict.fromkeys(PRIMARY, 0)), rc, timeout)):
                t = self.cargo.unsafe_metrics()
                self.assertFalse(t["valid"])
                self.assertIsNone(unsafe_primary_total(t))

    def test_valid_official_zero_remains_zero(self):
        self.cargo.cfg["unsafe_metrics"]["command"] = "analyzer"
        with patch("tools.run_cmd", return_value=execution(json.dumps({"totals": dict.fromkeys(PRIMARY, 0)}))):
            t = self.cargo.unsafe_metrics()
        self.assertTrue(t["valid"])
        self.assertEqual(unsafe_primary_total(t), 0)

    def test_clippy_nonzero_timeout_malformed_and_missing_completion(self):
        good = execution('{"reason":"build-finished","success":true}\n')
        bad_results = [execution("", 1), execution(good["stdout"], 0, True), execution("oops"), execution("")]
        for bad in bad_results:
            with self.subTest(bad=bad), patch.object(self.cargo, "_touch_sources"), patch.object(self.cargo, "_cargo", side_effect=[execution(), bad, good, good, good]):
                self.assertFalse(self.cargo.clippy()["ok"])

    def test_exact_assignment_clippy_failure_is_mandatory(self):
        good = execution('{"reason":"build-finished","success":true}\n')
        with patch.object(self.cargo, "_touch_sources"), patch.object(self.cargo, "_cargo", side_effect=[execution("", 1), good, good, good, good]) as call:
            self.assertFalse(self.cargo.clippy()["ok"])
            exact = call.call_args_list[0].args
            self.assertNotIn("-A", exact)
            self.assertIn("--all-features", exact)
            for group in CFG["clippy"]["groups"]:
                self.assertIn("clippy::" + group, exact)

    def test_all_clean_checks_reach_done(self):
        self.assertEqual(self.pipeline.phase_of(clean_state()), "DONE")

    def test_mandatory_validation_blocks_done(self):
        for mutate in (lambda s: s["test"].update(ok=False), lambda s: s["clippy"].update(ok=False),
                       lambda s: s.update(unsafe_total=None), lambda s: s["unsafe"].update(tool="builtin-approximation"),
                       lambda s: s["unsafe"].update(valid=False),
                       lambda s: s.update(policy=["forbidden"]), lambda s: s.update(interface=["bad signature"])):
            s = clean_state(); mutate(s)
            self.assertNotEqual(self.pipeline.phase_of(s), "DONE")

    def test_clippy_success_and_malformed_message_schema(self):
        good = execution('{"reason":"build-finished","success":true}\n')
        with patch.object(self.cargo, "_touch_sources"), patch.object(self.cargo, "_cargo", side_effect=[execution(), good, good, good, good]):
            self.assertTrue(self.cargo.clippy()["ok"])
        for value in (None, [], {"code": []}, {"code": {"code": 123}, "level": "warning", "message": "bad"}):
            bad = execution(json.dumps({"reason":"compiler-message", "message":value}) + "\n" + good["stdout"])
            with self.subTest(value=value), patch.object(self.cargo, "_touch_sources"), patch.object(self.cargo, "_cargo", side_effect=[execution(), bad, good, good, good]):
                self.assertFalse(self.cargo.clippy()["ok"])

    def test_interface_and_policy_rank_above_more_passing_tests(self):
        valid = clean_state()
        for field in ("policy", "interface"):
            invalid = clean_state(); invalid[field] = ["violation"]; invalid["passed"] = 999
            self.assertGreater(self.pipeline.score_of(valid), self.pipeline.score_of(invalid))

    def test_protected_files_are_anchored_to_skeleton(self):
        skeleton = self.root / "subject/rust_skeleton"; skeleton.mkdir(parents=True)
        crate = self.root / "crate"; crate.mkdir()
        (skeleton / "Cargo.toml").write_text("original")
        (crate / "Cargo.toml").write_text("tampered before run")
        ws = Workspace(crate, skeleton.parent, CFG); ws.snapshot_protected()
        self.assertTrue(ws.protected_violations())

    def test_symlink_edit_escape_refused(self):
        crate = self.root / "crate"; (crate / "src").mkdir(parents=True)
        (crate / "src/escape.rs").symlink_to(self.root / "outside.rs")
        ws = Workspace(crate, self.root, CFG)
        self.assertIsNotNone(ws.write_file("src/escape.rs", "bad"))
        self.assertFalse((self.root / "outside.rs").exists())

    def test_function_unsafe_qualifier_is_part_of_interface(self):
        self.assertTrue(interface_check.check_module("pub fn f(p: *const u8) {}", "pub unsafe fn f(p: *const u8) {}", "x"))


if __name__ == "__main__":
    unittest.main()
