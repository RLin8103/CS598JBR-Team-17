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
from tools import (  # noqa: E402
    CargoTools, Workspace, parse_reply, redact, salvage_partial, strip_fences, unsafe_primary_total,
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
        target_dir = Path(args.target_dir) if args.target_dir else Path.home() / ".cache" / "crust_target" / f"{self.name}"
        self.ws = Workspace(self.crate, self.subject, self.cfg)
        self.cargo = CargoTools(self.crate, self.toolchain, target_dir, self.cfg)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.log_root / f"run_{stamp}"
        self.events_path = self.run_dir / "trajectory.jsonl"
        self.history: list[dict] = []
        self.pending_partial: dict[str, dict] = {}  # files cut off mid-write by the output limit
        self.notes = ""
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
                shutil.rmtree(self.crate)
            shutil.copytree(skeleton, self.crate, ignore=shutil.ignore_patterns("target", ".git", ".DS_Store"))
            lib = (self.crate / "src" / "lib.rs").read_text(encoding="utf-8")
            for mod in re.findall(r"^\s*pub\s+mod\s+(\w+)\s*;", lib, re.M):
                dest = self.crate / "src" / f"{mod}.rs"
                iface = self.crate / "src" / "interfaces" / f"{mod}.rs"
                if not dest.exists() and not (self.crate / "src" / mod / "mod.rs").exists() and iface.exists():
                    shutil.copyfile(iface, dest)
        (self.crate / ".gitignore").write_text("target/\n", encoding="utf-8")
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
        copied = []
        for p in sorted(src_dir.rglob("*.rs")):
            rel = str(p.relative_to(src_dir)).replace("\\", "/")
            if self.ws.is_editable(rel):
                (self.crate / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, self.crate / rel)
                copied.append(rel)
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
        state["compiles"] = bool(state["build"]["ok"])
        t = state["test"] or {}
        state["passed"] = t.get("passed", 0)
        state["total"] = t.get("total", 0)
        state["failed"] = t.get("failed", 0)
        state["unsafe_total"] = unsafe_primary_total(state["unsafe"])
        c = state["clippy"]
        state["clippy_counts"] = c["counts"] if c else None
        state["clippy_total"] = c["total"] if c else None
        state["phase"] = self.phase_of(state)
        state["score"] = self.score_of(state)
        return state

    def phase_of(self, s: dict) -> str:
        if s["policy"]:
            return "POLICY"
        if not s["compiles"]:
            return "COMPILE"
        if s["failed"] > 0 or s["total"] == 0 or (s["test"] or {}).get("compile_failed"):
            return "TESTS"
        if s["unsafe_total"] > 0:
            return "SAFETY"
        accept = self.cfg["stopping_condition"]["clippy_accept"]
        if (s["clippy_total"] or 0) > accept:
            return "CLIPPY"
        return "DONE"

    @staticmethod
    def score_of(s: dict) -> tuple:
        errors = s["build"]["error_count"] if not s["compiles"] else 0
        return (
            int(s["compiles"]), s["passed"], -errors, -s["unsafe_total"],
            -(s["clippy_total"] if s["clippy_total"] is not None else 10_000),
        )

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
        for p in self.ws.editable_files():
            self.write_log(f"{d}/files/{self.ws.rel(p)}", p.read_text(encoding="utf-8", errors="replace"))
        rec = self.metric_record(it, state)
        self.metrics_log.append(rec)
        self.write_log(f"{d}/metrics.json", json.dumps(rec, indent=2))
        self.write_log("metrics_by_iteration.json", json.dumps(self.metrics_log, indent=2))
        self.log_event("checks", **rec)

    def metric_record(self, it: int, s: dict) -> dict:
        totals = s["unsafe"].get("totals", {})
        return {
            "iteration": it, "phase": s["phase"], "compiles": s["compiles"],
            "tests_passed": s["passed"], "tests_total": s["total"],
            "build_errors": s["build"]["error_count"],
            "clippy": s["clippy_counts"], "clippy_total": s["clippy_total"],
            "unsafe_primary": {k: totals.get(k, 0) for k in ("unsafe_lines", "unsafe_calls", "unsafe_casts", "pointer_arithmetic")},
            "unsafe_extra": {k: v for k, v in totals.items() if k not in ("unsafe_lines", "unsafe_calls", "unsafe_casts", "pointer_arithmetic")},
            "unsafe_tool": s["unsafe"].get("tool"),
            "policy_issues": s["policy"],
            "llm_tokens_so_far": self.llm.total_tokens,
        }

    # ------------------------------------------------------------------ prompt building
    def file_block(self, path: Path, label: str | None = None, limit: int | None = None) -> str:
        text = path.read_text(encoding="utf-8", errors="replace")
        lang = "rust" if path.suffix == ".rs" else "c" if path.suffix in (".c", ".h") else ""
        shown = cut(text, limit, "... [truncated; use <read> for the rest]") if limit else text
        return f"### {label or path.name} ({text.count(chr(10)) + 1} lines)\n{fence(shown, lang)}"

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
        t = s["unsafe"].get("totals", {})
        clippy = json.dumps(s["clippy_counts"]) if s["clippy_counts"] else "n/a (needs a successful build)"
        return (
            f"- compiles: {s['compiles']} ({s['build']['error_count']} errors)\n"
            f"- tests: {s['passed']} passed / {s['total']} total ({s['failed']} failed)\n"
            f"- unsafe metrics ({s['unsafe'].get('tool')}): lines={t.get('unsafe_lines', 0)}, calls={t.get('unsafe_calls', 0)}, "
            f"casts={t.get('unsafe_casts', 0)}, pointer_arithmetic={t.get('pointer_arithmetic', 0)}\n"
            f"- clippy warnings: {clippy}\n"
            f"- tokens used so far: {self.llm.total_tokens} / {self.limits['max_total_tokens']}"
        )

    def failure_details(self, t: dict) -> str:
        text = t["stdout"] + "\n" + t["stderr"]
        chunks = re.findall(r"---- (\S+) stdout ----\n(.*?)(?=\n---- \S+ stdout ----|\nfailures:\n|\Z)", text, re.S)
        lines = []
        for name, body in chunks[:12]:
            lines.append(f"[{name}]\n{cut(body.strip(), 900)}")
        return "\n\n".join(lines)

    def feedback_text(self, s: dict) -> str:
        cap = self.cfg["context"]["max_feedback_chars"]
        parts: list[str] = []
        if s["policy"]:
            parts.append("## Policy violations\n" + "\n".join(f"- {p}" for p in s["policy"]))
        b = s["build"]
        if not b["ok"]:
            parts.append("## cargo build errors\n" + fence(cut(b["pretty"], cap // 2, "... [more diagnostics omitted; fix these first]")))
        else:
            parts.append(f"## cargo build\nOK ({b.get('warning_count', 0)} rustc warnings).")
            t = s["test"]
            if t["compile_failed"]:
                parts.append("## cargo test\nThe test target failed to compile:\n" + fence(cut(t["stderr"], cap // 2)))
            else:
                head = f"## cargo test\n{t['passed']} passed, {t['failed']} failed, total {t['total']}."
                if t["timed_out"]:
                    head += f" The run hit the {self.cargo.test_timeout}s timeout (possible infinite loop)."
                if t["failing_tests"]:
                    head += "\nFailing: " + ", ".join(t["failing_tests"])
                    head += "\n\n" + fence(cut(self.failure_details(t), cap // 2))
                parts.append(head)
            c = s["clippy"]
            show_clippy = s["phase"] in ("CLIPPY", "SAFETY", "DONE") or c["total"] <= 25
            body = f"## cargo clippy\nCounts: {json.dumps(c['counts'])} (total {c['total']}). Target: 0 in every category."
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
        if s["unsafe_total"]:
            offs = u.get("offenders", [])[:30]
            body += "\nWhere:\n" + "\n".join(f"- {o['file']}:{o['line']} [{o['kind']}] {o['text']}" for o in offs)
            if not s["compiles"] or s["phase"] in ("COMPILE", "TESTS"):
                body += ("\nDo not add new unsafe code while fixing this. Replace raw-pointer helpers with safe code over "
                         "slices/`Vec`/iterators; keep unsafe, if a signature truly forces it, confined to that one function.")
        parts.append(body)
        return cut("\n\n".join(parts), cap * 2)

    def first_prompt(self, s: dict) -> str:
        tpl = (self.prompts / "task.md").read_text(encoding="utf-8")
        max_c = self.cfg["context"]["max_c_chars_in_first_prompt"]
        c_dir = self.subject / "c_source"
        c_blocks, used = [], 0
        for p in sorted(c_dir.rglob("*")):
            if p.is_file() and p.suffix in (".c", ".h") or p.name in ("Makefile", "README.md") and p.parent == c_dir:
                size = p.stat().st_size
                limit = None if used + size <= max_c else 2000
                c_blocks.append(self.file_block(p, f"c_source/{p.relative_to(c_dir)}".replace("\\", "/"), limit))
                used += min(size, 2000) if limit else size
        iface = [self.file_block(p, f"src/interfaces/{p.name}") for p in sorted((self.crate / "src" / "interfaces").glob("*.rs"))]
        tests = [self.file_block(p, f"src/bin/{p.name}") for p in sorted((self.crate / "src" / "bin").glob("*.rs"))]
        for k, v in {
            "PROJECT_NAME": self.name, "TOOLCHAIN": self.toolchain, "TREE": self.ws.tree(),
            "INTERFACE_FILES": "\n\n".join(iface), "TEST_FILES": "\n\n".join(tests),
            "C_FILES": "\n\n".join(c_blocks), "CURRENT_FILES": self.current_files(),
            "FEEDBACK": self.status_table(s) + "\n\n" + self.feedback_text(s),
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
        served_reads: set[str] = set()
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
                self.notes = parsed["notes"]
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
                for rel in parsed["reads"]:
                    if rel in served_reads:
                        served.append(f"### {rel}\n(already provided above in this turn - do not request it again; write your edits now)")
                        self.log_event("tool", iteration=it, tool="read_file_duplicate", path=rel)
                        continue
                    served_reads.add(rel)
                    text = self.ws.read_file(rel)
                    self.log_event("tool", iteration=it, tool="read_file", path=rel, chars=len(text))
                    served.append(f"### {rel}\n{fence(text)}")
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

    def restore(self, snap: dict[str, str]) -> None:
        for p in self.ws.editable_files():
            if self.ws.rel(p) not in snap:
                p.unlink()
        for rel, text in snap.items():
            (self.crate / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.crate / rel).write_text(text, encoding="utf-8")

    def run(self) -> int:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.setup_workspace()
        system = (self.prompts / "system.md").read_text(encoding="utf-8").replace("{{TOOLCHAIN}}", self.toolchain)
        self.write_log("config_used.json", json.dumps({**self.cfg, "llm_resolved": self.llm.describe(), "project": self.name}, indent=2))
        self.write_log("system_prompt.md", system)
        self.say(f"project={self.name} model={self.llm.model} toolchain={self.toolchain}")
        self.log_event("start", project=self.name, llm=self.llm.describe(), limits=self.limits)

        state = self.run_checks("baseline")
        self.save_checks(0, state)
        first = self.first_prompt(state)
        self.write_log("initial_prompt.md", first)
        best, best_snap, best_it = state["score"], self.best_snapshot(), 0
        stop_reason = "max_iterations"
        notices: list[str] = []
        done_streak = 0
        it = 0
        last_progress_it = 0
        try:
            while True:
                if state["phase"] == "DONE":
                    stop_reason = "success"
                    break
                if it >= self.limits["max_iterations"]:
                    stop_reason = "max_iterations"
                    break
                if self.llm.total_tokens >= self.limits["max_total_tokens"]:
                    stop_reason = "token_budget"
                    break
                if it - last_progress_it >= self.limits["no_progress_patience"]:
                    stop_reason = "no_progress"
                    break
                it += 1
                self.say(f"=== iteration {it}/{self.limits['max_iterations']} phase={state['phase']} score={state['score']}")
                # Iteration 1 is answered directly from the first prompt (task + baseline check).
                user_msg = None if it == 1 else self.feedback_prompt(it, state, notices)
                notices = []
                turn = self.agent_turn(it, system, first, user_msg)
                if turn["finish_reason"] == "length":
                    notices.append("Your previous reply hit the output token limit. Keep replies short: change a few functions per reply with <edit>, "
                                   "and never write more than ~250 lines in one <file>/<append> block.")
                for p in turn["problems"]:
                    notices.append(p)
                if turn["done"]:
                    done_streak += 1
                    if state["phase"] != "DONE":
                        notices.append(f"You sent <done/> but the targets are not met (phase {state['phase']}).")
                else:
                    done_streak = 0
                if self.pending_partial:
                    # A file was cut off mid-write: cargo would only report errors about the half-written file,
                    # so skip the checks and ask the model to finish it. Such turns do not count as "no progress".
                    notices.append(self.continuation_notice())
                    state = dict(state, label=f"iter {it} (file incomplete, checks skipped)")
                    last_progress_it = it
                elif turn["edits"]:
                    state = self.run_checks(f"iter {it}")
                else:
                    notices.append("No valid edit was applied in your previous reply." if not turn["done"] else "No edits were made.")
                    state = dict(state, label=f"iter {it} (unchanged)")
                self.save_checks(it, state)
                self.say(f"iteration {it}: phase={state['phase']} compiles={state['compiles']} tests={state['passed']}/{state['total']} "
                         f"unsafe={state['unsafe_total']} clippy={state['clippy_total']} tokens={self.llm.total_tokens}")
                if state["score"] > best:
                    best, best_snap, best_it = state["score"], self.best_snapshot(), it
                    last_progress_it = it
                elif turn["edits"]:
                    # The model is actively changing code (e.g. working through compile errors whose
                    # count may temporarily rise): that is activity, not a stall. Only score
                    # improvements update the best snapshot, but activity resets the patience clock.
                    last_progress_it = it
                if done_streak >= 2 and state["compiles"] and state["failed"] == 0 and state["total"] > 0:
                    stop_reason = "agent_done"
                    break
        except LLMError as exc:
            stop_reason = f"llm_error: {exc}"
            self.say(stop_reason)
        except KeyboardInterrupt:
            stop_reason = "interrupted"

        resumable = stop_reason.startswith("llm_error") or stop_reason == "interrupted"
        if resumable and best_it != it:
            # Rate limit / outage / Ctrl-C: keep the latest work in translations/ so that running the
            # pipeline again WITHOUT --fresh continues from here instead of from the empty skeleton.
            self.say("stopped early: keeping the latest Rust files in place; rerun without --fresh to continue")
        elif best_it != it:
            self.say(f"restoring best snapshot from iteration {best_it}")
            self.restore(best_snap)
            state = self.run_checks("final (best snapshot)")
            self.save_checks(it + 1, state)
        self.finish(state, stop_reason, it, best_it)
        if resumable:
            self.say("RESUME: bash MP4/src/run_pipeline.sh <project-id>   (no --fresh)")
        return 0 if state["phase"] == "DONE" else 1

    def finish(self, state: dict, stop_reason: str, iterations: int, best_it: int) -> None:
        rec = self.metric_record(iterations, state)
        final = {
            "project": self.name, "stop_reason": stop_reason, "agent_iterations": iterations,
            "best_iteration": best_it, "final": rec,
            "llm_calls": self.llm.calls, "prompt_tokens": self.llm.total_prompt_tokens,
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
    ap.add_argument("--fresh", action="store_true", help="discard the existing translation and start from the skeleton")
    ap.add_argument("--resume-from", default="", metavar="RUN:ITER",
                    help="continue from the agent's own Rust files saved in trajectories/<project>/RUN/iteration_ITER/files "
                         "(e.g. run_20261112_200435:9)")
    args = ap.parse_args()
    if not args.project_id and not (args.project and args.subject and args.out and args.log):
        ap.error("use --project-id N, or --project/--subject/--out/--log")
    return Pipeline(args).run()


if __name__ == "__main__":
    sys.exit(main())
