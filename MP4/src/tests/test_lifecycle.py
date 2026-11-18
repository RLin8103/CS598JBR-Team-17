"""Exercise real controller file retention/rollback with fake model/tool responses."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import Pipeline
from llm import LLMError
from tools import PRIMARY, parse_reply

ROOT = Path(__file__).resolve().parents[2]


class LifecycleTests(unittest.TestCase):
    def setup_pipeline(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        skeleton = root / "subject/rust_skeleton"
        (skeleton / "src/interfaces").mkdir(parents=True)
        (skeleton / "Cargo.toml").write_text('[package]\nname="fixture"\nversion="0.1.0"\nedition="2021"\n')
        (skeleton / "src/lib.rs").write_text("pub mod x;\n")
        (skeleton / "src/interfaces/x.rs").write_text("pub fn x() -> i32 { unimplemented!() }\n")
        import shutil
        shutil.copytree(skeleton, root / "crate")
        (root / "crate/src/x.rs").write_text("pub fn x() -> i32 { 1 }\n")
        cfg = json.loads((ROOT / "configs/pipeline.json").read_text())
        cfg["limits"].update(max_iterations=1, review_rounds=0)
        config = root / "config.json"; config.write_text(json.dumps(cfg))
        args = argparse.Namespace(project_id=None, project="fixture", subject=str(skeleton.parent),
            out=str(root / "crate"), log=str(root / "logs"), config=str(config), max_iterations=0,
            target_dir=str(root / "target"), fresh=False, resume_from="", repair_context="")
        pipeline = Pipeline(args)
        def checks(p, label):
            bad = "BAD" in (p.crate / "src/x.rs").read_text()
            totals = dict.fromkeys(PRIMARY, 0); totals["unsafe_lines"] = 1
            s = dict(label=label, policy=[], interface=[], stubs=[], compiles=not bad,
                passed=0 if bad else 1, failed=0, total=0 if bad else 1,
                build=dict(cmd="fake build", returncode=1 if bad else 0, timed_out=False, seconds=0,
                           stdout="", stderr="compile failure" if bad else "", pretty="compile failure" if bad else "", ok=not bad, error_count=int(bad)),
                test=None if bad else dict(cmd="fake test", returncode=0, timed_out=False, stdout="", stderr="", ok=True, valid_output=True, compile_failed=False,
                                          passed=1, failed=0, total=1, failing_tests=[]),
                clippy=None if bad else dict(counts=dict.fromkeys(cfg["clippy"]["groups"],0), total=0, rendered={}, ok=True),
                clippy_total=None if bad else 0, clippy_counts=None if bad else dict.fromkeys(cfg["clippy"]["groups"],0),
                unsafe={"tool":"official", "valid":True, "totals":totals, "offenders":[]}, unsafe_total=1, additional_checks=[])
            s["phase"] = p.phase_of(s); s["score"] = p.score_of(s)
            return s
        pipeline.run_checks = types.MethodType(checks, pipeline)
        return pipeline

    def test_indexed_prompt_prefers_complete_source_and_drops_stale_baseline(self):
        p = self.setup_pipeline()
        p.cfg["context"].update(mode="indexed", max_c_chars_in_first_prompt=200)
        root = p.subject / "c_source"
        root.mkdir()
        (root / "README.md").write_text("C manual " * 500)
        (root / "test.c").write_text("int main(void) { return 0; }\n")
        (root / "a.c").write_text("/* unrelated */ " * 30)
        (root / "x.h").write_text("int x(void);\n/* END OF HEADER */\n")
        state = p.run_checks("fixture baseline")
        prompt = p.first_prompt(state)
        self.assertIn("`c_source/x.h` (2 lines, included below)", prompt)
        self.assertIn("END OF HEADER", prompt)
        self.assertIn("`c_source/test.c` (1 lines, available via read)", prompt)
        self.assertNotIn("C manual", prompt)
        self.assertNotIn("int main(void)", prompt)
        self.assertNotIn("{{SOURCE_INDEX}}", prompt)
        p.history.append({"msgs": [{"role": "user", "content": "obsolete"}]})
        response = p.build_messages("system", prompt, [{"role": "user", "content": "current feedback"}])
        self.assertIn("END OF HEADER", response[1]["content"])
        self.assertNotIn("## Baseline check", response[1]["content"])
        self.assertEqual(response[-1]["content"], "current feedback")

    def test_reads_include_line_ranges_and_stay_inside_the_project(self):
        p = self.setup_pipeline()
        self.assertEqual(parse_reply('<read path="src/x.rs"/> <read path="src/x.rs" start="1" end="1"/>')["reads"],
                         [("src/x.rs", None, None), ("src/x.rs", 1, 1)])
        self.assertEqual(p.ws.read_file("src/x.rs", start=1, end=1), "pub fn x() -> i32 { 1 }\n")
        self.assertIn("inclusive range", p.ws.read_file("src/x.rs", start=2, end=1))
        self.assertIn("escapes", p.ws.read_file("../subject/rust_skeleton/src/lib.rs", start=1, end=1))
        (p.crate / "escape.rs").symlink_to(p.subject / "rust_skeleton/src/lib.rs")
        self.assertIn("escapes", p.ws.read_file("escape.rs"))

    def test_range_read_reaches_the_model_on_the_followup(self):
        p = self.setup_pipeline()
        p.limits["max_read_rounds_per_iteration"] = 1
        p.run_dir.mkdir(parents=True)
        (p.crate / "src/excerpt.rs").write_text("first\nmiddle\nlast\n")
        received = []

        def reply(messages):
            received.append(list(messages))
            content = '<read path="src/excerpt.rs" start="2" end="2"/>' if len(received) == 1 else "<done/>"
            return dict(content=content, model="fake-model", finish_reason="stop", usage={}, seconds=0)

        p.llm.chat = reply
        self.assertTrue(p.agent_turn(1, "system", "baseline", None)["done"])
        self.assertEqual(len(received), 2)
        followup = received[1][-1]["content"]
        self.assertIn("lines 2–2", followup)
        self.assertIn("middle", followup)
        self.assertNotIn("first", followup)
        self.assertNotIn("last", followup)

    def test_rejected_files_and_diagnostics_survive_rollback(self):
        p = self.setup_pipeline()
        p.llm.chat = lambda messages: dict(content='<file path="src/x.rs">BAD</file>', model="fake-model", finish_reason="stop", usage={}, seconds=0)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(p.run(), 1)
        self.assertIn("BAD", (p.run_dir / "iteration_01/files/src/x.rs").read_text())
        self.assertFalse(json.loads((p.run_dir / "iteration_01/validation.json").read_text())["compiles"])
        self.assertIn("{ 1 }", (p.crate / "src/x.rs").read_text())
        selected = json.loads((p.run_dir / "final_status.json").read_text())
        self.assertTrue(selected["final"]["compiles"])
        self.assertEqual(selected["final"]["implementation_sha256"], p.implementation_hashes())
        self.assertIn('"event": "rollback"', p.events_path.read_text())

    def test_conservative_repair_retains_named_gain(self):
        p = self.setup_pipeline()
        p.cfg["selection"] = "conservative_repair"
        original_checks = p.run_checks

        def checks(pipeline, label):
            state = original_checks(label)
            edited = "{ 2 }" in (pipeline.crate / "src/x.rs").read_text()
            state["additional_checks"] = [dict(
                ok=False, outcomes={"one": "ok" if edited else "FAILED", "two": "FAILED"},
                cmd="fixture regressions", returncode=1, timed_out=False, stdout="", stderr="",
            )]
            state["score"] = pipeline.score_of(state)
            return state

        p.run_checks = types.MethodType(checks, p)
        p.llm.chat = lambda messages: dict(content='<file path="src/x.rs">pub fn x() -> i32 { 2 }</file>',
                                           model="fake-model", finish_reason="stop", usage={}, seconds=0)
        with contextlib.redirect_stdout(io.StringIO()):
            p.run()
        self.assertIn("{ 2 }", (p.crate / "src/x.rs").read_text())
        status = json.loads((p.run_dir / "final_status.json").read_text())
        self.assertEqual(status["best_iteration"], 1)
        self.assertEqual(status["final"]["implementation_sha256"], p.implementation_hashes())
        self.assertEqual(status["final"]["regression_outcomes"], [{"one": "ok", "two": "FAILED"}])

    def test_partial_edits_before_api_failure_are_saved_then_best_restored(self):
        p = self.setup_pipeline()
        def fail(messages):
            (p.crate / "src/x.rs").write_text("BAD partial work")
            raise LLMError("fixture outage")
        p.llm.chat = fail
        with contextlib.redirect_stdout(io.StringIO()):
            p.run()
        self.assertEqual((p.run_dir / "interrupted_work/files/src/x.rs").read_text(), "BAD partial work")
        self.assertIn("{ 1 }", (p.crate / "src/x.rs").read_text())
        final = json.loads((p.run_dir / "final_status.json").read_text())
        self.assertEqual(final["completed_model_turns"], 0)
        self.assertEqual(final["attempted_iterations"], 1)
        self.assertEqual(final["final"]["implementation_sha256"], p.implementation_hashes())

    def test_keyboard_interrupt_restores_and_records_best(self):
        p = self.setup_pipeline()
        def fail(messages):
            (p.crate / "src/x.rs").write_text("BAD interrupted")
            raise KeyboardInterrupt
        p.llm.chat = fail
        with contextlib.redirect_stdout(io.StringIO()):
            p.run()
        self.assertIn("BAD", (p.run_dir / "interrupted_work/files/src/x.rs").read_text())
        self.assertIn("{ 1 }", (p.crate / "src/x.rs").read_text())
        self.assertEqual(json.loads((p.run_dir / "final_status.json").read_text())["stop_reason"], "interrupted")


if __name__ == "__main__":
    unittest.main()
