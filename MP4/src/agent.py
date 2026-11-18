#!/usr/bin/env python3
"""crust_agent: iterative agentic C -> Rust translation controller.

Cycle (per iteration):
    inspect C project / current Rust  ->  model edits Rust files  ->  cargo build
    -> cargo test -> cargo clippy (4 categories) -> unsafe metrics
    -> feedback goes back to the model  ->  repeat until the stopping condition.

The same controller is used for every project; nothing in here knows about individual C
functions. Project-specific context (C sources, Rust interface, tests) is supplied
automatically from the subject directory.

Usage:
    python3 src/agent.py --project-id 1          # cset  (see configs/projects.json)
    python3 src/agent.py --project-id 2          # libpsbt
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
MP4 = HERE.parent
sys.path.insert(0, str(HERE))

from llm import LLMClient, LLMError  # noqa: E402
from regression_results import run_additional_check
from tools import (  # noqa: E402
    CargoTools, Workspace, parse_reply, redact, safe_write, salvage_partial, strip_fences, unsafe_primary_total,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cut(text: str, limit: int, note: str = "... [truncated]") -> str:
    return text if len(text) <= limit else text[:limit] + "\n" + note


def fence(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text}\n```"


def compact_reply(text: str, limit: int = 8000) -> str:
    """Replace <file>/<append> bodies (even unclosed ones) by a marker; they are re-sent in the file listing."""
    def repl(m: re.Match) -> str:
        lines = m.group(3).count("\n") + 1
        return f'<{m.group(1)} path="{m.group(2)}">[{lines} lines omitted from history; see current files]</{m.group(1)}>'
    out = re.sub(r'<(file|append)\s+path="([^"]+)"\s*>(.*?)(?:</\1>|\Z)', repl, text, flags=re.S)
    return out if len(out) <= limit else out[:limit] + "\n... [reply truncated in history]"


class Pipeline:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.cfg = load_json(Path(args.config))
        projects = load_json(MP4 / "configs" / "projects.json")["projects"]
        if args.project_id:
            p = projects[str(args.project_id)]
            self.name = p["name"]
            self.subject = MP4 / p["subject"]
            self.crate = MP4 / p["translation"]
            self.log_root = MP4 / p["trajectory"]
        else:
            self.name = args.project
            self.subject = Path(args.subject).resolve()
            self.crate = Path(args.out).resolve()
            self.log_root = Path(args.log).resolve()
        if args.max_iterations:
            self.cfg["limits"]["max_iterations"] = args.max_iterations
        self.limits = self.cfg["limits"]
        self.toolchain = self.cfg["toolchain"]
        self.prompts = MP4 / "configs" / "prompts"
        self.phase_text = load_json(self.prompts / "phases.json")
        self.llm = LLMClient(self.cfg["llm"])
        target_dir = Path(args.target_dir) if args.target_dir else MP4 / ".runtime" / "target" / self.name
        self.ws = Workspace(self.crate, self.subject, self.cfg)
        self.cargo = CargoTools(self.crate, self.toolchain, target_dir, self.cfg)
        self.check_sequence = 0
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.run_dir = self.log_root / f"run_{stamp}"
        self.events_path = self.run_dir / "trajectory.jsonl"
        self.llm.on_event = lambda kind, **data: self.log_event(kind, **data)
        self.history: list[dict] = []
        self.pending_partial: dict[str, dict] = {}  # files cut off mid-write by the output limit
        self.notes = ""
        self.reference_context: str | None = None
        self.metrics_log: list[dict] = []
        self.secrets = self.llm.secrets()

    # ------------------------------------------------------------------ logging
    def log_event(self, kind: str, **data) -> None:
        rec = {"t": datetime.now().isoformat(timespec="seconds"), "event": kind, **data}
        with self.events_path.open("a", encoding="utf-8") as fh:
            fh.write(redact(json.dumps(rec, ensure_ascii=False), self.secrets) + "\n")

    def write_log(self, rel: str, text: str) -> None:
        path = self.run_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(redact(text, self.secrets), encoding="utf-8")

    def say(self, msg: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with (self.run_dir / "pipeline.log").open("a", encoding="utf-8") as fh:
            fh.write(redact(line, self.secrets) + "\n")

    # ------------------------------------------------------------------ workspace setup
    def setup_workspace(self) -> None:
        skeleton = self.subject / "rust_skeleton"
        if not skeleton.is_dir():
            raise SystemExit(f"missing {skeleton}")
        fresh = self.args.fresh or not (self.crate / "Cargo.toml").exists()
        if fresh:
            if self.crate.exists():
                shutil.copytree(self.crate, self.run_dir / "pre_fresh_workspace",
                                ignore=shutil.ignore_patterns("target", ".git"))
                shutil.rmtree(self.crate)
            shutil.copytree(skeleton, self.crate, ignore=shutil.ignore_patterns("target", ".git", ".DS_Store"))
            lib = (self.crate / "src" / "lib.rs").read_text(encoding="utf-8")
            for mod in re.findall(r"^\s*pub\s+mod\s+(\w+)\s*;", lib, re.M):
                dest = self.crate / "src" / f"{mod}.rs"
                iface = self.crate / "src" / "interfaces" / f"{mod}.rs"
                if not dest.exists() and not (self.crate / "src" / mod / "mod.rs").exists() and iface.exists():
                    shutil.copyfile(iface, dest)
        self.ws.snapshot_protected()
        if self.args.resume_from:
            self.resume_from_snapshot(self.args.resume_from)

    def resume_from_snapshot(self, spec: str) -> None:
        """Continue from the Rust files the agent itself produced in an earlier iteration (RUN:ITER).

        Used after a controller/provider interruption so the agent's own earlier work is not lost.
        Only editable files are copied; the event is logged in this run's trajectory.
        """
        run, _, n = spec.partition(":")
        src_dir = self.log_root / run / f"iteration_{int(n):02d}" / "files"
        if not src_dir.is_dir():
            raise SystemExit(f"--resume-from: {src_dir} not found")
        snapshot = {}
        for p in sorted(src_dir.rglob("*.rs")):
            rel = str(p.relative_to(src_dir)).replace("\\", "/")
            if self.ws.is_editable(rel):
                snapshot[rel] = p.read_text(encoding="utf-8")
        if not snapshot:
            raise SystemExit("resume snapshot has no editable source files")
        self.restore(snapshot)
        copied = sorted(snapshot)
        self.say(f"resumed from {run} iteration {n}: restored {copied}")
        self.log_event("resume_from", source_run=run, source_iteration=int(n), files=copied)

    # ------------------------------------------------------------------ checks
    def run_checks(self, label: str) -> dict:
        state: dict = {"label": label}
        state["policy"] = self.ws.protected_violations() + self.ws.forbidden_findings()
        self.say(f"{label}: cargo build")
        state["build"] = self.cargo.build()
        if state["build"]["ok"]:
            self.say(f"{label}: cargo test")
            state["test"] = self.cargo.test()
            self.say(f"{label}: cargo clippy (4 categories)")
            state["clippy"] = self.cargo.clippy()
        else:
            state["test"] = None
            state["clippy"] = None
        self.say(f"{label}: unsafe metrics")
        state["unsafe"] = self.cargo.unsafe_metrics()
        state["additional_checks"] = []
        for command in self.cfg.get("additional_checks", []):
            self.check_sequence += 1
            output = self.run_dir / "additional_checks" / str(self.check_sequence)
            state["additional_checks"].append(run_additional_check(
                command, output=output, project_id=self.args.project_id, crate=self.crate,
                mp4=MP4, python=sys.executable, env=self.cargo.env, timeout=self.limits["command_timeout_s"],
            ))
        state["compiles"] = bool(state["build"]["ok"])
        t = state["test"] or {}
        state["passed"] = t.get("passed", 0)
        state["total"] = t.get("total", 0)
        state["failed"] = t.get("failed", 0)
        state["unsafe_total"] = unsafe_primary_total(state["unsafe"])
        state["stubs"] = self.ws.stub_findings()
        state["interface"] = self.ws.interface_findings()
        c = state["clippy"]
        state["clippy_counts"] = c["counts"] if c else None
        state["clippy_total"] = c["total"] if c else None
        def interrupted(value):
            if isinstance(value, dict):
                return value.get("interrupted") is True or any(interrupted(v) for v in value.values())
            if isinstance(value, list):
                return any(interrupted(v) for v in value)
            return False
        state["interrupted"] = interrupted(state)
        state["phase"] = self.phase_of(state)
        state["score"] = self.score_of(state)
        return state

    def phase_of(self, s: dict) -> str:
        if s["policy"]:
            return "POLICY"
        if not s["compiles"]:
            return "COMPILE"
        if s["interface"]:
            # The CRUST-Bench interface is part of the specification: signatures must stay exactly as given.
            return "INTERFACE"
        if s["stubs"] and (s["failed"] == 0 or s["passed"] > 0):
            # Untranslated bodies remain although the code compiles (and the tests either pass or the failures are
            # not about missing code): finish the translation of the modules the tests do not exercise.
            return "STUBS"
        if not (s["test"] or {}).get("ok"):
            return "TESTS"
        if not (s["clippy"] or {}).get("ok"):
            return "VALIDATION"
        if any(not c.get("ok") for c in s.get("additional_checks", [])):
            return "REGRESSIONS"
        if s["unsafe_total"] is None or s["unsafe"].get("valid") is not True:
            return "VALIDATION"
        if s["unsafe_total"] > 0:
            return "SAFETY"
        if s["unsafe"].get("tool") != "official":
            return "VALIDATION"
        accept = self.cfg["stopping_condition"]["clippy_accept"]
        if s["clippy_total"] is None or s["clippy_total"] > accept:
            return "CLIPPY"
        return "DONE"

    @staticmethod
    def score_of(s: dict) -> tuple:
        errors = s["build"]["error_count"] if not s["compiles"] else 0
        return (
            int(not s["policy"]), -len(s["policy"]), -len(s["interface"]),
            int(s["compiles"]), int(bool((s["test"] or {}).get("valid_output"))),
            int(bool((s["test"] or {}).get("ok"))), s["passed"], -s["failed"], -errors, -len(s["stubs"]),
            -sum(not c.get("ok") for c in s.get("additional_checks", [])),
            int(bool((s["clippy"] or {}).get("ok"))),
            int(s["unsafe_total"] is not None), -(s["unsafe_total"] if s["unsafe_total"] is not None else 10_000),
            -(s["clippy_total"] if s["clippy_total"] is not None else 10_000),
        )

    @staticmethod
    def repair_rejection(candidate: dict, selected: dict) -> str | None:
        """Compare complete observations for autonomous repair continuations."""
        if candidate["policy"] or candidate["interface"] or not candidate["compiles"]:
            return "candidate violates policy/interface or failed to build"
        current = candidate["test"] or {}
        previous = selected["test"] or {}
        if (not current.get("valid_output") or current.get("timed_out") or current.get("interrupted")
                or current.get("returncode") != (101 if candidate["failed"] else 0)
                or set(current.get("test_results", {})) != set(previous.get("test_results", {}))
                or candidate["passed"] < selected["passed"] or candidate["total"] != selected["total"]):
            return "benchmark status, coverage or passing count regressed"
        lost = [name for name, count in previous.get("test_results", {}).items()
                if current["test_results"][name] < count]
        if lost:
            return "benchmark passes lost: " + ", ".join(lost)
        if not (candidate["clippy"] or {}).get("ok"):
            return "Clippy did not complete successfully"
        if (candidate["unsafe"].get("tool") != selected["unsafe"].get("tool")
                or (selected["unsafe"].get("valid") and not candidate["unsafe"].get("valid"))):
            return "safety evidence regressed"
        before = selected["additional_checks"]
        after = candidate["additional_checks"]
        if not before or len(before) != len(after):
            return "regression comparison unavailable"
        gains = []
        for old, new in zip(before, after):
            old_cases, new_cases = old.get("outcomes"), new.get("outcomes")
            if not old_cases or not new_cases or old_cases.keys() != new_cases.keys():
                return "regression results unavailable, invalid or incomplete"
            lost = [name for name, status in old_cases.items() if status == "ok" and new_cases[name] != "ok"]
            if lost:
                return "regression passes lost: " + ", ".join(lost)
            gains.extend(name for name, status in old_cases.items() if status == "FAILED" and new_cases[name] == "ok")
        if gains or candidate["score"] > selected["score"]:
            return None
        return "no measured improvement"

    def save_checks(self, it: int, state: dict) -> None:
        d = f"iteration_{it:02d}"
        b = state["build"]
        self.write_log(f"{d}/build.txt", f"$ {b['cmd']}\nreturncode={b['returncode']} seconds={b['seconds']}\n\n{b['stderr']}")
        if state["test"]:
            t = state["test"]
            self.write_log(f"{d}/test.txt", f"$ {t['cmd']}\nreturncode={t['returncode']} timed_out={t['timed_out']}\n\n{t['stdout']}\n{t['stderr']}")
        if state["clippy"]:
            c = state["clippy"]
            parts = [f"# Clippy counts: {json.dumps(c['counts'])} total={c['total']}"]
            for g, msgs in c["rendered"].items():
                parts.append(f"\n## {g} ({len(msgs)})\n" + "\n".join(msgs))
            self.write_log(f"{d}/clippy.txt", "\n".join(parts))
        self.write_log(f"{d}/unsafe_metrics.json", json.dumps(state["unsafe"], indent=2))
        self.write_log(f"{d}/validation.json", json.dumps(state, indent=2))
        for p in self.ws.editable_files():
            self.write_log(f"{d}/files/{self.ws.rel(p)}", p.read_text(encoding="utf-8", errors="replace"))
        rec = self.metric_record(it, state)
        self.metrics_log.append(rec)
        self.write_log(f"{d}/metrics.json", json.dumps(rec, indent=2))
        self.write_log("metrics_by_iteration.json", json.dumps(self.metrics_log, indent=2))
        self.log_event("checks", **rec)

    def metric_record(self, it: int, s: dict) -> dict:
        totals = s["unsafe"].get("totals") or {}
        return {
            "iteration": it, "phase": s["phase"], "compiles": s["compiles"],
            "tests_passed": s["passed"], "tests_total": s["total"],
            "build_errors": s["build"]["error_count"], "stubs_remaining": len(s["stubs"]), "interface_deviations": len(s["interface"]),
            "clippy": s["clippy_counts"], "clippy_total": s["clippy_total"],
            "unsafe_primary": {k: totals.get(k) for k in ("unsafe_lines", "unsafe_calls", "unsafe_casts", "pointer_arithmetic")},
            "unsafe_extra": {k: v for k, v in totals.items() if k not in ("unsafe_lines", "unsafe_calls", "unsafe_casts", "pointer_arithmetic")},
            "unsafe_tool": s["unsafe"].get("tool"),
            "policy_issues": s["policy"],
            "test_ok": bool((s["test"] or {}).get("ok")),
            "test_returncode": (s["test"] or {}).get("returncode"),
            "test_timed_out": (s["test"] or {}).get("timed_out"),
            "test_valid_output": (s["test"] or {}).get("valid_output"),
            "distinct_tests_passed": (s["test"] or {}).get("distinct_passed"),
            "distinct_tests_total": (s["test"] or {}).get("distinct_total"),
            "clippy_ok": bool((s["clippy"] or {}).get("ok")),
            "unsafe_valid": s["unsafe"].get("valid", False),
            "additional_checks_ok": [c["ok"] for c in s.get("additional_checks", [])],
            "regression_outcomes": [c.get("outcomes") for c in s.get("additional_checks", [])],
            "implementation_sha256": self.implementation_hashes(),
            "llm_tokens_so_far": self.llm.total_tokens,
        }

    # ------------------------------------------------------------------ prompt building
    def file_block(self, path: Path, label: str | None = None, limit: int | None = None) -> str:
        text = path.read_text(encoding="utf-8", errors="replace")
        lang = "rust" if path.suffix == ".rs" else "c" if path.suffix in (".c", ".h") else ""
        shown = cut(text, limit, "... [truncated; use <read> for the rest]") if limit else text
        return f"### {label or path.name} ({text.count(chr(10)) + 1} lines)\n{fence(shown, lang)}"

    @property
    def indexed_context(self) -> bool:
        return self.cfg["context"].get("mode") == "indexed"

    def indexed_c_files(self, evidence: str) -> tuple[str, str]:
        """Index all supplied C files and fill the budget with complete production sources."""
        root = self.subject / "c_source"
        paths = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in (".c", ".h"))
        rust_modules = {p.stem for p in self.ws.editable_files()}
        cited = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\.rs:\d+", evidence))

        def is_test(path):
            rel = path.relative_to(root)
            words = re.split(r"[_-]", path.stem.lower())
            return "test" in words or "tests" in words or any(d.lower() in ("test", "tests") for d in rel.parts[:-1])

        priority = sorted(paths, key=lambda p: (p.stem not in cited, p.stem not in rust_modules, p))
        budget = self.cfg["context"]["max_c_chars_in_first_prompt"]
        index, blocks = [], []
        for path in priority:
            text = path.read_text(encoding="utf-8", errors="replace")
            rel = f"c_source/{path.relative_to(root).as_posix()}"
            inline = not is_test(path) and len(text) <= budget
            if inline:
                blocks.append(self.file_block(path, rel))
                budget -= len(text)
            index.append(f"- `{rel}` ({len(text.splitlines())} lines, {'included below' if inline else 'available via read'})")
        return "\n".join(index), "\n\n".join(blocks) or "(Use the source index to request files.)"

    def current_files(self, mentioned: str = "") -> str:
        budget = self.cfg["context"]["max_file_chars_in_prompt"]
        files = self.ws.editable_files()
        out, used = [], 0
        ordered = sorted(files, key=lambda p: (Path(p).name not in mentioned, p.name))
        for p in ordered:
            rel = self.ws.rel(p)
            size = p.stat().st_size
            if used + size <= budget or Path(p).name in mentioned:
                out.append(self.file_block(p, rel))
                used += size
            else:
                out.append(self.file_block(p, rel, limit=1500) + "\n(file shown only partially to save context; use <read path=\"" + rel + "\"/> for all of it)")
                used += 1500
        out.sort(key=lambda b: b.split("\n", 1)[0])
        return "\n\n".join(out) if out else "(no editable files)"

    def status_table(self, s: dict) -> str:
        t = s["unsafe"].get("totals") or {}
        clippy = json.dumps(s["clippy_counts"]) if s["clippy_counts"] else "n/a (needs a successful build)"
        return (
            f"- compiles: {s['compiles']} ({s['build']['error_count']} errors)\n"
            f"- tests: {s['passed']} passed / {s['total']} total ({s['failed']} failed)\n"
            f"- unsafe metrics ({s['unsafe'].get('tool')}): lines={t.get('unsafe_lines')}, calls={t.get('unsafe_calls')}, "
            f"casts={t.get('unsafe_casts')}, pointer_arithmetic={t.get('pointer_arithmetic')}\n"
            f"- validation: test_ok={(s['test'] or {}).get('ok')}, clippy_ok={(s['clippy'] or {}).get('ok')}, unsafe_valid={s['unsafe'].get('valid')}\n"
            f"- clippy warnings: {clippy}\n"
            f"- interface deviations (signatures that differ from src/interfaces/*.rs): {len(s['interface'])}\n"
            f"- untranslated bodies (`unimplemented!()`/`todo!()`): {len(s['stubs'])}"
            + ("".join(f"\n  - {x}" for x in s["stubs"][:15]) if s["stubs"] else "") + "\n"
            f"- tokens used so far: {self.llm.total_tokens}"
        )

    def failure_details(self, t: dict, *, all_cases: bool = False) -> str:
        text = t["stdout"] + "\n" + t["stderr"]
        chunks = re.findall(r"---- (\S+) stdout ----\n(.*?)(?=\n---- \S+ stdout ----|\nfailures:\n|\Z)", text, re.S)
        lines = []
        for name, body in (chunks if all_cases else chunks[:12]):
            if all_cases:
                body = re.sub(r"^note: run with `RUST_BACKTRACE=1`.*$", "", body, flags=re.M)
                body = body.replace(str(self.crate) + "/", "").replace(str(MP4) + "/", "")
                if "outcomes" in t:
                    body = re.sub(r"(panicked at )src/lib.rs:", r"\g<1>evaluation/harness/src/lib.rs:", body)
            lines.append(f"[{name}]\n{cut(body.strip(), 600 if all_cases else 900)}")
        return "\n\n".join(dict.fromkeys(lines) if all_cases else lines)

    def feedback_text(self, s: dict) -> str:
        cap = self.cfg["context"]["max_feedback_chars"]
        parts: list[str] = []
        if s["policy"]:
            parts.append("## Policy violations\n" + "\n".join(f"- {p}" for p in s["policy"]))
        if s["interface"]:
            parts.append("## Interface deviations (the interface files are part of the specification and hidden tests are compiled against them)\n"
                         + "\n".join(f"- {x}" for x in s["interface"][:14])
                         + ("\n- ... more omitted" if len(s["interface"]) > 14 else "")
                         + "\nRestore every signature, struct/enum definition and `impl` header exactly as in `src/interfaces/`. "
                           "Do not add or remove generic bounds, change `&self`/`&mut self`, or change parameter or return types to make the body easier. "
                           "If a signature cannot be implemented soundly, document a precise counterexample. Moving unsafe operations into helpers does not establish soundness.")
        b = s["build"]
        if not b["ok"]:
            parts.append("## cargo build errors\n" + fence(cut(b["pretty"], cap // 2, "... [more diagnostics omitted; fix these first]")))
        else:
            parts.append(f"## cargo build\nOK ({b.get('warning_count', 0)} rustc warnings).")
            t = s["test"]
            if t["compile_failed"]:
                parts.append("## cargo test\nThe test target failed to compile:\n" + fence(cut(t["stderr"], cap // 2)))
            else:
                head = f"## cargo test\n{t['passed']} passed, {t['failed']} failed, total {t['total']}. returncode={t['returncode']} valid_output={t['valid_output']} ok={t['ok']}\n"
                if not t["ok"] and (not self.indexed_context or not t["valid_output"] or not t["failing_tests"]):
                    head += fence(cut(t['stdout'] + '\n' + t['stderr'], cap // 2))
                if t["timed_out"]:
                    head += f" The run hit the {self.cargo.test_timeout}s timeout (possible infinite loop)."
                if t["failing_tests"]:
                    head += "\nFailing: " + ", ".join(t["failing_tests"])
                    head += "\n\n" + fence(cut(self.failure_details(t, all_cases=self.indexed_context), cap // 2))
                parts.append(head)
            c = s["clippy"]
            show_clippy = s["phase"] in ("CLIPPY", "SAFETY", "DONE") or c["total"] <= 25
            body = f"## cargo clippy\nCounts: {json.dumps(c['counts'])} (total {c['total']}). Target: 0 in every category."
            if not c["ok"]:
                body += "\nExecution failed/incomplete; warning counts are not a clean result.\n" + fence(cut(json.dumps(c), cap // 2))
            if show_clippy and c["total"]:
                shown, n = [], 0
                for g in ("correctness", "complexity", "perf", "style"):
                    for m in c["rendered"].get(g, []):
                        if n >= 14:
                            break
                        shown.append(f"[{g}] {cut(m, 700)}")
                        n += 1
                body += "\n" + fence(cut("\n\n".join(shown), cap // 2, "... [more findings omitted]"))
            parts.append(body)
        u = s["unsafe"]
        tot = u.get("totals", {})
        body = "## unsafe metrics (" + str(u.get("tool")) + ")\n" + json.dumps(tot)
        if s["unsafe_total"] is None or u.get("tool") != "official":
            body += "\nMandatory official safety validation unavailable/invalid: " + str(u.get("error", "official analyzer not configured"))
        for name, detail in u.get("diagnostics", {}).items():
            if detail.strip():
                body += "\nOfficial NewMetrics " + name + ":\n" + fence(detail)
        if s["unsafe_total"]:
            offs = u.get("offenders", [])[:30]
            body += "\nWhere:\n" + "\n".join(f"- {o['file']}:{o['line']} [{o['kind']}] {o['text']}" for o in offs)
            if not s["compiles"] or s["phase"] in ("COMPILE", "TESTS"):
                body += ("\nDo not add new unsafe code while fixing this. Replace raw-pointer helpers with safe code over "
                         "slices/`Vec`/iterators; keep unsafe, if a signature truly forces it, confined to that one function.")
        parts.append(body)
        regression_parts = []
        for check in s.get("additional_checks", []):
            outcomes = check.get("outcomes")
            summary = json.dumps(outcomes, sort_keys=True) if outcomes else check.get("validation_error", "")
            details = self.failure_details(check, all_cases=self.indexed_context) if outcomes else check["stdout"] + "\n" + check["stderr"]
            command = "" if self.indexed_context else f"$ {check['cmd']}\n"
            regression_parts.append(
                f"## Separate regression check\n{command}returncode={check['returncode']} timed_out={check['timed_out']}\n"
                + summary + "\n" + fence(cut(details, cap))
            )
        return cut("\n\n".join(parts), cap) + "\n\n" + cut("\n\n".join(regression_parts), cap)

    def first_prompt(self, s: dict) -> str:
        tpl = (self.prompts / "task.md").read_text(encoding="utf-8")
        feedback = self.feedback_text(s)
        index = ""
        if self.indexed_context:
            index, c_files = self.indexed_c_files(feedback)
        else:
            max_c = self.cfg["context"]["max_c_chars_in_first_prompt"]
            c_dir = self.subject / "c_source"
            c_blocks, used = [], 0
            for p in sorted(c_dir.rglob("*")):
                if p.is_file() and p.suffix in (".c", ".h") or p.name in ("Makefile", "README.md") and p.parent == c_dir:
                    size = p.stat().st_size
                    limit = None if used + size <= max_c else 2000
                    c_blocks.append(self.file_block(p, f"c_source/{p.relative_to(c_dir)}".replace("\\", "/"), limit))
                    used += min(size, 2000) if limit else size
            c_files = "\n\n".join(c_blocks)
        iface = [self.file_block(p, f"src/interfaces/{p.name}") for p in sorted((self.crate / "src" / "interfaces").glob("*.rs"))]
        tests = [self.file_block(p, f"src/bin/{p.name}") for p in sorted((self.crate / "src" / "bin").glob("*.rs"))
                 if not self.indexed_context or not (s["test"] or {}).get("ok")]
        test_files = "\n\n".join(tests) or "Read benchmark source on demand using paths in the workspace tree."
        if self.indexed_context:
            self.reference_context = (
                f"# Project: {self.name}\n\n"
                f"## Source index\n{index}\n\n"
                f"## Frozen Rust interfaces\n" + "\n\n".join(iface) +
                f"\n\n## Original C implementation\n{c_files}\n\n"
                "Use the latest controller message for the current Rust and check results. "
                "Continue from the selected snapshot and choose a focused repair based on the observations."
            )
        for k, v in {
            "PROJECT_NAME": self.name, "TOOLCHAIN": self.toolchain, "TREE": self.ws.tree(),
            "INTERFACE_FILES": "\n\n".join(iface), "TEST_FILES": test_files,
            "C_FILES": c_files, "CURRENT_FILES": self.current_files(feedback if self.indexed_context else ""),
            "SOURCE_INDEX": "## Source index\n" + index + "\n\n" if index else "",
            "TASK": ("Continue from the existing agent-generated implementation. Select a failure from the diagnostics, "
                     "inspect the C and Rust, record your hypothesis in notes, and propose a focused edit. Use the next "
                     "validation result to decide whether to revise it or inspect another failure."
                     if self.cfg.get("selection") == "conservative_repair" else
                     "Implement the C behavior across all required Rust modules. Study the source, interface and tests first."),
            "FEEDBACK": self.status_table(s) + "\n\n" + feedback,
        }.items():
            tpl = tpl.replace("{{" + k + "}}", v)
        return tpl

    def feedback_prompt(self, it: int, s: dict, notices: list[str]) -> str:
        tpl = (self.prompts / "feedback.md").read_text(encoding="utf-8")
        fb = self.feedback_text(s)
        phase = "CONTINUE" if self.pending_partial else s["phase"]
        notice_txt = ("## Notices from the controller\n" + "\n".join(f"- {n}" for n in notices) + "\n\n") if notices else ""
        notes_txt = f"## Your notes from the previous turn\n{self.notes}\n\n" if self.notes else ""
        for k, v in {
            "ITERATION": str(it), "MAX_ITERATIONS": str(self.limits["max_iterations"]),
            "NOTICES": notice_txt + notes_txt, "STATUS_TABLE": self.status_table(s),
            "PHASE": phase, "PHASE_INSTRUCTIONS": self.phase_text[phase],
            "FEEDBACK": fb, "CURRENT_FILES": self.current_files(fb),
        }.items():
            tpl = tpl.replace("{{" + k + "}}", v)
        return tpl

    def build_messages(self, system: str, first: str, current: list[dict]) -> list[dict]:
        if self.history and self.reference_context is not None:
            return [{"role": "system", "content": system}, {"role": "user", "content": self.reference_context}, *current]
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": first}]
        keep = self.cfg["context"]["keep_full_turns"]
        older = self.history[:-keep] if keep else self.history
        recent = self.history[-keep:] if keep else []
        for h in older:
            if h["user_short"] is not None:
                msgs.append({"role": "user", "content": h["user_short"]})
            msgs.append({"role": "assistant", "content": h["assistant_short"]})
        for h in recent:
            msgs.extend(h["msgs"])
        msgs.extend(current)
        return msgs

    # ------------------------------------------------------------------ one agent turn
    def agent_turn(self, it: int, system: str, first: str, user_msg: str) -> dict:
        turn_msgs: list[dict] = []
        if user_msg is not None:
            turn_msgs.append({"role": "user", "content": user_msg})
            self.write_log(f"iteration_{it:02d}/user_0.md", user_msg)
        edits_applied: list[str] = []
        problems: list[str] = []
        reply_all: list[str] = []
        served_reads: set[tuple[str, int | None, int | None]] = set()
        done = False
        finish_reason = None
        for round_no in range(self.limits["max_read_rounds_per_iteration"] + 1):
            messages = self.build_messages(system, first, turn_msgs)
            resp = self.llm.chat(messages)
            finish_reason = resp["finish_reason"]
            content = resp["content"]
            reply_all.append(content)
            # The full reply is logged; the conversation history keeps a compact copy (file bodies are
            # re-sent fresh in every feedback message, so storing them again would only waste context).
            turn_msgs.append({"role": "assistant", "content": compact_reply(content)})
            self.write_log(f"iteration_{it:02d}/assistant_{round_no}.md", content)
            self.log_event("llm", iteration=it, round=round_no, model=resp["model"], usage=resp["usage"], finish_reason=finish_reason,
                           seconds=resp["seconds"], reply_chars=len(content))
            parsed = parse_reply(content)
            if parsed["notes"] is not None:
                self.notes = cut(parsed["notes"], 3000, "... [notes cut: keep them short]")
            if parsed["malformed_edits"]:
                problems.append(
                    f"{parsed['malformed_edits']} <edit> block(s) in your previous reply were ignored because they were malformed. "
                    "Exact format: <edit path=\"src/x.rs\"><search>old text</search><replace>new text</replace></edit> "
                    "(all four tags, closed in order; <search> must match the current file text exactly, including indentation).")
                self.log_event("tool", iteration=it, tool="malformed_edit", count=parsed["malformed_edits"])
            for kind, rel, body in parsed["ops"]:
                if kind == "file":
                    err, label = self.ws.write_file(rel, body), f"wrote {rel}"
                elif kind == "append":
                    err, label = self.ws.append_file(rel, body), f"appended to {rel}"
                else:
                    err, label = self.ws.edit_file(rel, body[0], body[1]), f"edited {rel}"
                (problems if err else edits_applied).append(err or label)
                if not err and kind in ("file", "append"):
                    self.pending_partial.pop(rel.strip().removeprefix("./"), None)  # block closed: file finished
                self.log_event("tool", iteration=it, tool=f"{kind}_file" if kind != "edit" else "edit_file", path=rel, error=err,
                               chars=len(body) if isinstance(body, str) else len(body[1]))
            trunc = parsed["truncated"]
            if trunc and finish_reason != "length":
                # Reply finished normally but the closing tag is missing/wrong: accept the block as complete.
                kind, rel, body = trunc
                body = strip_fences(body)
                if body.strip():
                    err = self.ws.write_file(rel, body) if kind == "file" else self.ws.append_file(rel, body)
                    (problems if err else edits_applied).append(err or f"wrote {rel} (closing tag missing, accepted)")
                    if not err:
                        self.pending_partial.pop(rel.strip().removeprefix("./"), None)
                    self.log_event("tool", iteration=it, tool=f"{kind}_file_unclosed", path=rel, error=err, chars=len(body))
                trunc = None
            if trunc and finish_reason == "length":
                kind, rel, partial = trunc
                kept, n_lines, last_line = salvage_partial(partial)
                rel = rel.strip().removeprefix("./")
                if kept.strip():
                    err = self.ws.write_file(rel, kept) if kind == "file" else self.ws.append_file(rel, kept)
                    if err:
                        problems.append(err)
                    else:
                        edits_applied.append(f"saved partial {rel} ({n_lines} lines of this reply, cut off by the output limit)")
                        self.pending_partial[rel] = {"last_line": last_line}
                        self.log_event("tool", iteration=it, tool="partial_save", path=rel, lines=n_lines)
            done = done or parsed["done"]
            if parsed["reads"] and not parsed["ops"] and not trunc and round_no < self.limits["max_read_rounds_per_iteration"]:
                served = []
                remaining = self.cfg["context"].get("max_read_chars", 60000 * len(parsed["reads"]))
                for read in parsed["reads"]:
                    rel, start, end = read
                    label = f"{rel} (lines {start}–{end})" if start is not None else rel
                    if read in served_reads:
                        served.append(f"### {label}\n(already provided above in this turn)")
                        continue
                    if remaining <= 0:
                        served.append(f"### {label}\n(read budget exhausted; request a narrower range)")
                        break
                    served_reads.add(read)
                    text = self.ws.read_file(rel, min(remaining, 60000), start, end)
                    remaining -= len(text)
                    self.log_event("tool", iteration=it, tool="read_file", path=rel, start=start, end=end, chars=len(text))
                    served.append(f"### {label}\n{fence(text)}")
                follow = "Requested files:\n\n" + "\n\n".join(served) + "\n\nNow write your edits in this same turn. Do not reply with only <read> blocks again."
                turn_msgs.append({"role": "user", "content": follow})
                self.write_log(f"iteration_{it:02d}/user_{round_no + 1}.md", follow)
                continue
            break
        short_user = None if it == 1 else f"(iteration {it}: controller feedback omitted to save context; current files are in the latest message)"
        short_asst = ("(earlier turn) " + ("; ".join(edits_applied) if edits_applied else "no edits")
                      + (f"\nnotes: {self.notes}" if self.notes else ""))
        self.history.append({"msgs": turn_msgs, "user_short": short_user, "assistant_short": short_asst})
        return {"edits": edits_applied, "problems": problems, "done": done, "finish_reason": finish_reason,
                "reply": "\n".join(reply_all), "pending": dict(self.pending_partial)}

    def continuation_notice(self) -> str:
        parts = []
        for rel, info in self.pending_partial.items():
            path = self.crate / rel
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
            tail = "\n".join(lines[-12:])
            parts.append(
                f"Your previous reply was cut off by the output-token limit while writing `{rel}`. The controller saved everything up to "
                f"the last complete line (the file now has {len(lines)} lines; the last saved line is `{info['last_line']}`). "
                f"Continue the file with <append path=\"{rel}\"> starting at the very next line. Do not repeat saved lines and do not re-send the "
                f"whole file. Keep each block below ~250 lines and finish the file. The crate will not compile until the file is complete.\n"
                f"Last saved lines:\n{fence(tail, 'rust')}"
            )
        return "\n\n".join(parts)

    # ------------------------------------------------------------------ main loop
    def best_snapshot(self) -> dict[str, str]:
        return {self.ws.rel(p): p.read_text(encoding="utf-8") for p in self.ws.editable_files()}

    def implementation_hashes(self) -> dict[str, str]:
        return {self.ws.rel(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.ws.editable_files()}

    def restore(self, snap: dict[str, str]) -> None:
        for p in self.ws.editable_files():
            if self.ws.rel(p) not in snap:
                p.unlink()
        for rel, text in snap.items():
            (self.crate / rel).parent.mkdir(parents=True, exist_ok=True)
            safe_write(self.crate / rel, text)

    def replay_candidate(self, spec: str, baseline: dict) -> int:
        """Re-evaluate an exact previously logged model edit without using inference."""
        run, _, number = spec.partition(":")
        if Path(run).name != run or not run.startswith("run_") or not number.isdecimal():
            raise SystemExit("--replay-candidate must name a local RUN:ITER")
        source = self.log_root / run / f"iteration_{int(number):02d}"
        expected = load_json(source / "metrics.json")["implementation_sha256"]
        saved = {p.relative_to(source / "files").as_posix(): p.read_text(encoding="utf-8")
                 for p in (source / "files").rglob("*.rs")}
        if (not saved or any(not self.ws.is_editable(rel) for rel in saved)
                or {rel: hashlib.sha256(content.encode()).hexdigest() for rel, content in saved.items()} != expected):
            raise SystemExit("Logged candidate files do not match the recorded implementation")
        original = self.best_snapshot()
        selected = 0
        reason = "candidate evaluation did not complete"
        self.log_event("candidate_replay", source_run=run, source_iteration=int(number), source_hashes=expected)
        try:
            self.restore(saved)
            candidate = self.run_checks("replayed candidate")
            self.save_checks(1, candidate)
            reason = "candidate validation interrupted" if candidate.get("interrupted") else self.repair_rejection(candidate, baseline)
            if reason is None:
                selected = 1
        finally:
            if selected == 0:
                self.restore(original)
        self.write_log("iteration_01/selection.json", json.dumps({
            "retained": selected == 1, "reason": reason, "selected_hashes": self.implementation_hashes(),
        }, indent=2))
        final = self.run_checks("final (selected replay snapshot)")
        self.save_checks(2, final)
        self.finish(final, "candidate_replay", 0, selected)
        return int(final["phase"] != "DONE")

    def preview_context(self, output: Path) -> int:
        """Record a real baseline and its initial prompt without starting a model run."""
        if not (self.crate / "Cargo.toml").is_file():
            raise SystemExit("Preview requires an existing translation")
        self.run_dir = output.resolve()
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.events_path = self.run_dir / "trajectory.jsonl"
        self.ws.snapshot_protected()
        self.write_log("config_used.json", json.dumps(self.cfg, indent=2))
        system = (self.prompts / "system.md").read_text(encoding="utf-8").replace("{{TOOLCHAIN}}", self.toolchain)
        self.write_log("system_prompt.md", system)
        state = self.run_checks("preview baseline")
        self.save_checks(0, state)
        self.write_log("initial_prompt.md", self.first_prompt(state))
        if self.reference_context is not None:
            self.write_log("reference_context.md", self.reference_context)
        return int(state.get("interrupted", False))

    def run(self) -> int:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.setup_workspace()
        shutil.copytree(self.prompts, self.run_dir / "prompt_templates")
        self.prompts = self.run_dir / "prompt_templates"
        self.phase_text = load_json(self.prompts / "phases.json")
        for source in HERE.glob("*.py"):
            target = self.run_dir / "controller_snapshot" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        system = (self.prompts / "system.md").read_text(encoding="utf-8").replace("{{TOOLCHAIN}}", self.toolchain)
        self.write_log("config_used.json", json.dumps({**self.cfg, "llm_resolved": self.llm.describe(), "project": self.name}, indent=2))
        self.write_log("system_prompt.md", system)
        self.say(f"project={self.name} model={self.llm.model} toolchain={self.toolchain}")
        self.log_event("start", project=self.name, llm=self.llm.describe(), limits=self.limits)
        self.write_log("provenance.json", json.dumps({
            "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob("*.py")},
            "initial_implementation_sha256": self.implementation_hashes(),
            "python": sys.version,
        }, indent=2))

        state = self.run_checks("baseline")
        self.save_checks(0, state)
        if state.get("interrupted"):
            self.finish(state, "interrupted", 0, 0)
            return 1
        if getattr(self.args, "replay_candidate", ""):
            return self.replay_candidate(self.args.replay_candidate, state)
        first = self.first_prompt(state)
        if self.args.repair_context:
            context = Path(self.args.repair_context).read_text(encoding="utf-8")
            self.write_log("repair_context.md", context)
            first += "\n\n## Targeted repair context\n" + context
        self.write_log("initial_prompt.md", first)
        if self.reference_context is not None:
            self.write_log("reference_context.md", self.reference_context)
        best, best_snap, best_it, best_state = state["score"], self.best_snapshot(), 0, state
        conservative = self.cfg.get("selection") == "conservative_repair"
        stop_reason = "max_iterations"
        notices: list[str] = []
        done_streak = 0
        no_edit_streak = 0
        it = 0
        last_progress_it = 0
        review_rounds = self.limits.get("review_rounds", 2)
        reviews_done = 0
        review_prior = "TESTS"
        force_review = False
        try:
            while True:
                if state["phase"] == "DONE" and reviews_done >= review_rounds:
                    stop_reason = "success"
                    break
                if state.get("interrupted"):
                    stop_reason = "interrupted"
                    break
                if it >= self.limits["max_iterations"]:
                    stop_reason = "max_iterations"
                    break
                token_limit = self.limits.get("max_total_tokens")
                if token_limit is not None and self.llm.total_tokens >= token_limit:
                    stop_reason = "token_budget"
                    break
                stalled = it - last_progress_it >= self.limits["no_progress_patience"]
                if reviews_done < review_rounds and (state["phase"] == "DONE" or stalled or force_review):
                    # Everything the automatic checks can see is done (or stuck): ask the model to compare its code with
                    # the C sources for behaviour the visible tests do not cover (hidden tests exercise the same API).
                    reviews_done += 1
                    force_review = False
                    last_progress_it = it
                    review_prior = state["phase"]
                    state = dict(state, phase="REVIEW")
                    self.log_event("review_round", iteration=it + 1, round=reviews_done, prior_phase=review_prior)
                elif stalled:
                    stop_reason = "no_progress"
                    break
                was_review = state["phase"] == "REVIEW"
                checked_now = False
                rejection = None
                it += 1
                self.say(f"=== iteration {it}/{self.limits['max_iterations']} phase={state['phase']} score={state['score']}")
                # Iteration 1 is answered directly from the first prompt (task + baseline check).
                user_msg = None if it == 1 else self.feedback_prompt(it, state, notices)
                notices = []
                turn = self.agent_turn(it, system, first, user_msg)
                self.log_event("completed_turn", iteration=it, edits=len(turn["edits"]))
                if turn["finish_reason"] == "length":
                    notices.append("Your previous reply hit the output token limit. Keep replies short: change a few functions per reply with <edit>, "
                                   "and never write more than ~250 lines in one <file>/<append> block.")
                for p in turn["problems"]:
                    notices.append(p)
                if turn["done"]:
                    done_streak += 1
                    if state["phase"] not in ("DONE", "REVIEW"):
                        notices.append(f"You sent <done/> but the targets are not met (phase {state['phase']}).")
                else:
                    done_streak = 0
                if self.pending_partial:
                    # A file was cut off mid-write: cargo would only report errors about the half-written file,
                    # so skip the checks and ask the model to finish it. Such turns do not count as "no progress".
                    notices.append(self.continuation_notice())
                    state = dict(state, label=f"iter {it} (file incomplete, checks skipped)")
                    for rel, content in self.best_snapshot().items():
                        self.write_log(f"iteration_{it:02d}/incomplete_files/{rel}", content)
                    self.log_event("checks_skipped", iteration=it, reason="incomplete_file", hashes=self.implementation_hashes())
                    last_progress_it = it
                elif turn["edits"]:
                    no_edit_streak = 0
                    prev_phase = state["phase"]
                    state = self.run_checks(f"iter {it}")
                    checked_now = True
                    # Save the rejected files with their diagnostics before any rollback.
                    self.save_checks(it, state)
                    if conservative:
                        rejection = self.repair_rejection(state, best_state)
                    elif prev_phase in ("INTERFACE", "SAFETY", "CLIPPY", "REVIEW") and state["score"] < best:
                        rejection = "validation score worsened during refinement"
                    if rejection:
                        # Refinement phases must never lose ground: undo an edit that broke the build/tests
                        # or made unsafe/Clippy worse, and tell the model so it tries a different change.
                        notices.append(
                            f"Your edit was rejected because {rejection} (compiles={state['compiles']}, tests {state['passed']}/{state['total']}, "
                            f"unsafe {state['unsafe_total']} vs {best_state['unsafe_total']}, clippy {state['clippy_total']} vs {best_state['clippy_total']}) "
                            "and was reverted. The files below are the last good version; try a different, smaller change.")
                        if not state["compiles"]:
                            notices.append("What went wrong in the reverted attempt (cargo build output):\n"
                                           + fence(cut(state["build"]["pretty"], 3500, "... [more diagnostics omitted]")))
                        elif (state["test"] or {}).get("compile_failed"):
                            notices.append("The reverted attempt made the test target fail to compile:\n"
                                           + fence(cut(state["test"]["stderr"], 3000)))
                        elif state["failed"]:
                            notices.append("The reverted attempt broke these tests: " + ", ".join(state["test"]["failing_tests"][:8])
                                           + "\n" + fence(cut(self.failure_details(state["test"]), 2500)))
                        if conservative:
                            notices.append("Validation of the rejected edit:\n" + self.feedback_text(state))
                        self.log_event("rollback", iteration=it, reason=rejection, rejected_hashes=self.implementation_hashes(),
                                       worse_score=list(state["score"]), restored_score=list(best))
                        self.restore(best_snap)
                        state = self.run_checks(f"iter {it} (edit reverted)")
                        checked_now = False
                else:
                    if not turn["done"]:
                        no_edit_streak += 1
                    notices.append("No valid edit was applied in your previous reply. Write an <edit> block now; keep <notes> short."
                                   if not turn["done"] else "No edits were made.")
                    if no_edit_streak >= 2 and self.llm.escalate(f"{no_edit_streak} replies in a row without an applied edit"):
                        notices.append("(The controller switched you to a different model after repeated replies without edits.)")
                        self.log_event("escalate", iteration=it, model=self.llm.model)
                        no_edit_streak = 0
                    state = dict(state, label=f"iter {it} (unchanged)")
                if was_review:
                    if not turn["edits"]:
                        reviews_done = review_rounds  # the review found nothing to change: no further rounds
                    elif reviews_done < review_rounds:
                        force_review = True  # run the next review round right away
                    if reviews_done >= review_rounds:
                        last_progress_it = it - self.limits["no_progress_patience"]  # reviews are over: stop unless this turn improves the score
                    if state["phase"] == "REVIEW":  # no checks were re-run, so the real phase is the one before the review
                        state = dict(state, phase=review_prior)
                if not turn["edits"] and not self.pending_partial:
                    self.save_checks(it, state)
                self.write_log(f"iteration_{it:02d}/selection.json", json.dumps({
                    "retained": checked_now if conservative else (checked_now and state["score"] >= best),
                    "reason": rejection, "pending_partial": bool(self.pending_partial),
                    "selected_hashes": self.implementation_hashes(), "selected_phase": state["phase"],
                }, indent=2))
                self.say(f"iteration {it}: phase={state['phase']} compiles={state['compiles']} tests={state['passed']}/{state['total']} "
                         f"unsafe={state['unsafe_total']} clippy={state['clippy_total']} tokens={self.llm.total_tokens}")
                improved = checked_now if conservative else state["score"] > best
                if improved or (not conservative and checked_now and state["score"] == best and state["compiles"]):
                    # An edit that keeps the score (e.g. a review fix for a panic the tests do not cover) must
                    # not be lost when the final snapshot is restored.
                    best, best_snap, best_it, best_state = state["score"], self.best_snapshot(), it, state
                if improved:
                    last_progress_it = it
                elif turn["edits"] and state["phase"] in ("COMPILE", "POLICY", "STUBS"):
                    # The model is actively changing code (e.g. working through compile errors whose
                    # count may temporarily rise): that is activity, not a stall. Only score
                    # improvements update the best snapshot, but activity resets the patience clock.
                    last_progress_it = it
                if done_streak >= 2 and state["phase"] == "DONE":
                    stop_reason = "agent_done"
                    break
        except LLMError as exc:
            stop_reason = f"llm_error: {exc}"
            self.say(stop_reason)
        except KeyboardInterrupt:
            stop_reason = "interrupted"

        resumable = stop_reason.startswith("llm_error") or stop_reason == "interrupted"
        if resumable:
            for rel, content in self.best_snapshot().items():
                self.write_log(f"interrupted_work/files/{rel}", content)
            self.log_event("interrupted_work_saved", reason=stop_reason, hashes=self.implementation_hashes())
        if self.best_snapshot() != best_snap:
            self.say(f"restoring best snapshot from iteration {best_it}")
            self.restore(best_snap)
            self.log_event("final_restore", source_iteration=best_it, reason=stop_reason)
        # Evaluate the exact selected files even on API failure or interruption.
        state = self.run_checks("final (selected snapshot)")
        self.save_checks(it + 1, state)
        self.finish(state, stop_reason, it, best_it)
        if resumable:
            self.say("Selected best snapshot restored; interrupted_work/ retains the unvalidated work for inspection.")
        return 0 if state["phase"] == "DONE" and stop_reason in ("success", "agent_done") else 1

    def finish(self, state: dict, stop_reason: str, iterations: int, best_it: int) -> None:
        rec = self.metric_record(iterations, state)
        final = {
            "project": self.name, "stop_reason": stop_reason, "agent_iterations": iterations,
            "best_iteration": best_it, "final": rec,
            "llm_calls": self.llm.calls, "prompt_tokens": self.llm.total_prompt_tokens,
            "attempted_iterations": iterations,
            "completed_model_turns": len(self.history),
            "successful_model_responses": self.llm.calls,
            "api_calls_attempted": self.llm.attempted_calls,
            "api_responses": self.llm.api_responses,
            "reported_cost_usd": self.llm.reported_cost_usd,
            "completion_tokens": self.llm.total_completion_tokens,
            "model": self.llm.model, "toolchain": self.toolchain,
        }
        self.write_log("final_status.json", json.dumps(final, indent=2))
        self.log_event("stop", **final)
        (self.log_root / "latest_run.txt").write_text(self.run_dir.name + "\n", encoding="utf-8")
        self.say(f"STOP: {stop_reason} | iterations={iterations} (best {best_it}) | compiles={state['compiles']} "
                 f"tests={state['passed']}/{state['total']} unsafe={state['unsafe_total']} clippy={state['clippy_total']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-id", type=int, choices=[1, 2], help="project number from configs/projects.json")
    ap.add_argument("--project", help="project name (when not using --project-id)")
    ap.add_argument("--subject", help="subject dir containing c_source/ and rust_skeleton/")
    ap.add_argument("--out", help="output crate dir (final Rust translation)")
    ap.add_argument("--log", help="trajectory dir")
    ap.add_argument("--config", default=str(MP4 / "configs" / "pipeline.json"))
    ap.add_argument("--max-iterations", type=int, default=0)
    ap.add_argument("--target-dir", default="", help="cargo target dir (default ~/.cache/crust_target/<project>)")
    ap.add_argument("--repair-context", default="", help="project-specific observed defects; saved with the run")
    ap.add_argument("--fresh", action="store_true", help="discard the existing translation and start from the skeleton")
    ap.add_argument("--resume-from", default="", metavar="RUN:ITER",
                    help="continue from the agent's own Rust files saved in trajectories/<project>/RUN/iteration_ITER/files "
                         "(e.g. run_20261112_200435:9)")
    ap.add_argument("--replay-candidate", default="", metavar="RUN:ITER",
                    help="compare an exact saved agent edit against current files offline")
    ap.add_argument("--preview-context", type=Path, help="save baseline evidence and prompts offline in a new directory")
    args = ap.parse_args()
    if args.preview_context and (args.fresh or args.resume_from or args.repair_context or args.replay_candidate):
        ap.error("--preview-context requires the existing baseline without other run modifiers")
    if args.replay_candidate and (args.fresh or args.resume_from or args.repair_context):
        ap.error("--replay-candidate requires the existing baseline without other run modifiers")
    if not args.project_id and not (args.project and args.subject and args.out and args.log):
        ap.error("use --project-id N, or --project/--subject/--out/--log")
    pipeline = Pipeline(args)
    return pipeline.preview_context(args.preview_context) if args.preview_context else pipeline.run()


if __name__ == "__main__":
    sys.exit(main())
