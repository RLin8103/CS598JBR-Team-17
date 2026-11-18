"""Tool layer for the agent: run cargo, parse results, run safety analysis, guarded file edits.

Everything the model learns about the crate comes from these functions, so the feedback it
receives matches what the instructional team will see (pinned toolchain, same Clippy flags).
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import interface_check  # noqa: E402  (same directory)

HERE = Path(__file__).resolve().parent


# ----------------------------------------------------------------------------- process runner
def run_cmd(cmd: list[str], cwd: Path, env: dict, timeout: int) -> dict:
    started = time.time()
    try:
        proc = subprocess.Popen(
            cmd, cwd=str(cwd), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, errors="replace", start_new_session=True,
        )
    except OSError as exc:
        return {"cmd": shlex.join(cmd), "returncode": None, "stdout": "", "stderr": str(exc),
                "seconds": round(time.time() - started, 2), "timed_out": False, "launch_error": str(exc)}
    timed_out = False
    interrupted = False
    try:
        out, err = proc.communicate(timeout=timeout)
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
        timed_out = isinstance(exc, subprocess.TimeoutExpired)
        interrupted = isinstance(exc, KeyboardInterrupt)
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        out, err = proc.communicate()
    return {
        "cmd": " ".join(shlex.quote(c) for c in cmd),
        "returncode": proc.returncode,
        "stdout": out or "",
        "stderr": err or "",
        "seconds": round(time.time() - started, 2),
        "timed_out": timed_out,
        "interrupted": interrupted,
    }


def cargo_env(target_dir: Path) -> dict:
    env = os.environ.copy()
    runtime = HERE.parent / ".runtime"
    if (runtime / "cargo" / "bin" / "cargo").exists():
        env["CARGO_HOME"] = str(runtime / "cargo")
        env["RUSTUP_HOME"] = str(runtime / "rustup")
    cargo_bin = str(Path(env.get("CARGO_HOME", Path.home() / ".cargo")) / "bin")
    if cargo_bin not in env.get("PATH", ""):
        env["PATH"] = cargo_bin + os.pathsep + env.get("PATH", "")
    env["CARGO_TARGET_DIR"] = str(target_dir)
    env["CARGO_TERM_COLOR"] = "never"
    env["RUST_BACKTRACE"] = "0"
    env["CARGO_INCREMENTAL"] = "0"
    return env


class CargoTools:
    def __init__(self, crate: Path, toolchain: str, target_dir: Path, cfg: dict):
        self.crate = crate
        self.toolchain = toolchain
        self.env = cargo_env(target_dir)
        self.cfg = cfg
        self.cmd_timeout = cfg["limits"]["command_timeout_s"]
        self.test_timeout = cfg["limits"]["test_timeout_s"]
        self.groups = cfg["clippy"]["groups"]
        self.clippy_extra = cfg["clippy"]["extra_args"]

    def _cargo(self, *args: str, timeout: int | None = None) -> dict:
        return run_cmd(["cargo", f"+{self.toolchain}", *args], self.crate, self.env, timeout or self.cmd_timeout)

    # ------------------------------------------------------------------ build
    def build(self) -> dict:
        res = self._cargo("build", "--all-targets")
        errors = [l for l in res["stderr"].splitlines()
                  if re.match(r"error(\[E\d+\])?:", l) and "could not compile" not in l and "aborting due to" not in l]
        res["ok"] = process_ok(res)
        res["error_count"] = len(errors)
        res["warning_count"] = sum(1 for l in res["stderr"].splitlines() if l.startswith("warning:") and "generated" not in l)
        res["pretty"] = "" if res["ok"] else res["stderr"]
        return res

    # ------------------------------------------------------------------ tests
    def test(self) -> dict:
        res = self._cargo("test", "--no-fail-fast", timeout=self.test_timeout)
        text = res["stdout"] + "\n" + res["stderr"]
        passed = failed = ignored = 0
        summaries = list(re.finditer(r"^test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;", text, re.M))
        for m in summaries:
            passed += int(m.group(2))
            failed += int(m.group(3))
            ignored += int(m.group(4))
        failing = sorted(set(re.findall(r"^test (\S+) \.\.\. FAILED", text, re.M)))
        passing = sorted(set(re.findall(r"^test (\S+) \.\.\. ok", text, re.M)))
        starts = [int(n) for n in re.findall(r"^running (\d+) tests?$", text, re.M)]
        # Every started harness must close, including zero-test/doc-test targets.
        records = re.findall(r"^test (\S+) \.\.\. (ok|FAILED|ignored)(?: .*)?$", text, re.M)
        valid = bool(summaries) and len(starts) == len(summaries)
        valid = valid and all(n == sum(int(m.group(i)) for i in (2, 3, 4, 5)) for n, m in zip(starts, summaries))
        valid = valid and len(records) == passed + failed + ignored
        valid = valid and all((m.group(1) == "ok") == (int(m.group(3)) == 0) for m in summaries)
        res.update({
            "passed": passed, "failed": failed, "ignored": ignored, "total": passed + failed,
            "failing_tests": failing, "passing_tests": passing,
            "compile_failed": ("could not compile" in text) and passed + failed == 0,
            "valid_output": bool(valid),
            "ok": process_ok(res) and bool(valid) and failed == 0 and passed > 0,
            "distinct_passed": len(passing), "distinct_failed": len(failing),
            "distinct_total": len(set(passing + failing)),
            "harnesses_started": starts, "harnesses_completed": len(summaries),
        })
        return res

    # ------------------------------------------------------------------ clippy
    def _touch_sources(self) -> None:
        now = time.time()
        for p in (self.crate / "src").rglob("*.rs"):
            os.utime(p, (now, now))

    def clippy(self) -> dict:
        """Run each Clippy category separately so counts are reported independently."""
        counts: dict[str, int] = {}
        rendered: dict[str, list[str]] = {}
        raw_logs: dict[str, str] = {}
        executions: dict[str, dict] = {}
        self._touch_sources()
        exact = self._cargo("clippy", "--all-targets", "--all-features", "--",
                            *[arg for g in ("correctness", "style", "complexity", "perf") for arg in ("-W", f"clippy::{g}")])
        for group in self.groups:
            self._touch_sources()  # make cargo re-run clippy with different lint flags
            res = self._cargo(
                "clippy", *self.clippy_extra, "--message-format=json", "--", "-A", "clippy::all", "-W", f"clippy::{group}"
            )
            seen = set()
            msgs: list[str] = []
            valid_json = True
            finished = False
            for line in res["stdout"].splitlines():
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    valid_json = False
                    continue
                if not isinstance(obj, dict):
                    valid_json = False
                    continue
                if obj.get("reason") == "build-finished":
                    finished = obj.get("success") is True
                if obj.get("reason") != "compiler-message":
                    continue
                m = obj.get("message")
                if not isinstance(m, dict):
                    valid_json = False
                    continue
                code_info = m.get("code") or {}
                if not isinstance(code_info, dict):
                    valid_json = False
                    continue
                code = code_info.get("code") or ""
                if not isinstance(code, str) or not isinstance(m.get("level"), str) or not isinstance(m.get("message"), str):
                    valid_json = False
                    continue
                if not code.startswith("clippy::") or m.get("level") not in ("warning", "error"):
                    continue
                text = m.get("rendered") or m.get("message", "")
                if not isinstance(text, str):
                    valid_json = False
                    continue
                if text in seen:
                    continue
                seen.add(text)
                msgs.append(text.strip())
            counts[group] = len(msgs)
            rendered[group] = msgs
            raw_logs[group] = res["stderr"][-3000:]
            res["valid_output"] = valid_json and finished
            res["ok"] = process_ok(res) and res["valid_output"]
            executions[group] = res
        ok = process_ok(exact) and all(r["ok"] for r in executions.values())
        return {
            "counts": counts, "total": sum(counts.values()), "rendered": rendered,
            "ok": ok, "compile_failed": not ok, "raw_stderr_tail": raw_logs,
            "exact_command": exact, "executions": executions,
        }

    # ------------------------------------------------------------------ safety
    def unsafe_metrics(self) -> dict:
        command = self.cfg["unsafe_metrics"].get("command")
        if command:
            cmd = shlex.split(command.replace("{path}", str(self.crate)))
            res = run_cmd(cmd, self.crate, self.env, self.cmd_timeout)
            try:
                data = json.loads(res["stdout"])
                totals = data.get("totals", data) if isinstance(data, dict) else None
                error = metrics_schema_error(totals)
                if isinstance(data, dict) and "offenders" in data and not isinstance(data["offenders"], list):
                    error = "optional offenders must be a list"
                if not process_ok(res):
                    error = "official analyzer execution failed or timed out"
                return {"tool": "official", "totals": totals if not error else None,
                        "offenders": data.get("offenders", []) if isinstance(data, dict) else [],
                        "execution": res, "valid": error is None, "error": error}
            except json.JSONDecodeError as exc:
                return {"tool": "official", "totals": None, "offenders": [], "execution": res,
                        "valid": False, "error": f"invalid official analyzer JSON: {exc}"}
        sys.path.insert(0, str(HERE))
        import unsafe_check  # noqa: WPS433 (local import keeps the module optional)
        data = unsafe_check.analyse(self.crate)
        data["valid"] = metrics_schema_error(data.get("totals")) is None
        data["official_available"] = False
        return data


PRIMARY = ("unsafe_lines", "unsafe_calls", "unsafe_casts", "pointer_arithmetic")


def process_ok(result: dict) -> bool:
    return type(result.get("returncode")) is int and result["returncode"] == 0 and result.get("timed_out") is False and not result.get("launch_error") and not result.get("interrupted")


def metrics_schema_error(totals) -> str | None:
    if not isinstance(totals, dict):
        return "unsafe metrics must be an object"
    for key in PRIMARY:
        if key not in totals or type(totals[key]) is not int or totals[key] < 0:
            return f"missing/invalid nonnegative integer metric: {key}"
    return None


def unsafe_primary_total(metrics: dict) -> int | None:
    totals = metrics.get("totals")
    if not metrics.get("valid") or metrics_schema_error(totals):
        return None
    return sum(totals[k] for k in PRIMARY)


# ----------------------------------------------------------------------------- guarded workspace
def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def glob_match(rel: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        return rel.startswith(pattern[:-3] + "/")
    return fnmatch.fnmatch(rel, pattern)


def safe_write(path: Path, text: str) -> None:
    """write_text with retries: files under /mnt/c (WSL) are occasionally locked for a moment by Windows
    (editor, indexer, antivirus), which surfaces as OSError EINVAL/EACCES."""
    last: OSError | None = None
    for attempt in range(10):
        try:
            path.write_text(text, encoding="utf-8")
            return
        except OSError as exc:
            last = exc
            time.sleep(0.3 * (attempt + 1))
    raise last  # type: ignore[misc]


class Workspace:
    """Crate directory plus the guard rails: protected files cannot be modified by the agent."""

    def __init__(self, crate: Path, subject: Path, cfg: dict):
        self.crate = crate
        self.subject = subject
        self.cfg = cfg
        self.protected_patterns = cfg["protected_paths"]
        self.editable_patterns = cfg["editable_globs"]
        self.forbidden = cfg["forbidden_patterns"]
        self.protected_hashes: dict[str, str] = {}

    # ----- paths
    def rel(self, p: Path) -> str:
        return str(p.relative_to(self.crate)).replace("\\", "/")

    def is_protected(self, rel: str) -> bool:
        return any(glob_match(rel, pat) for pat in self.protected_patterns)

    def is_editable(self, rel: str) -> bool:
        if self.is_protected(rel) or ".." in rel.split("/") or rel.startswith("/") or "\\" in rel:
            return False
        target = self.crate / rel
        if not target.resolve().is_relative_to(self.crate.resolve()):
            return False
        if any(p.is_symlink() for p in (target, *target.parents) if p.is_relative_to(self.crate)):
            return False
        return any(glob_match(rel, pat) for pat in self.editable_patterns)

    def editable_files(self) -> list[Path]:
        out = []
        src = self.crate / "src"
        if src.exists():
            for p in sorted(src.rglob("*.rs")):
                if self.is_editable(self.rel(p)):
                    out.append(p)
        return out

    def snapshot_protected(self) -> None:
        """Use the supplied skeleton as the trust anchor, not the current translation."""
        self.protected_hashes = {}
        skeleton = self.subject / "rust_skeleton"
        for p in sorted(skeleton.rglob("*")):
            if p.is_file() and "target" not in p.relative_to(skeleton).parts:
                rel = p.relative_to(skeleton).as_posix()
                if self.is_protected(rel):
                    self.protected_hashes[rel] = sha256_file(p)

    def protected_violations(self) -> list[str]:
        problems = []
        for rel, digest in self.protected_hashes.items():
            p = self.crate / rel
            if not p.exists():
                problems.append(f"protected file deleted: {rel}")
            elif sha256_file(p) != digest:
                problems.append(f"protected file modified: {rel}")
        for p in self.crate.rglob("*"):
            if "target" in p.relative_to(self.crate).parts:
                continue
            if p.is_file() and self.is_protected(self.rel(p)) and self.rel(p) not in self.protected_hashes:
                problems.append(f"new file in protected area: {self.rel(p)}")
        if (self.crate / "build.rs").exists():
            problems.append("build.rs present (forbidden)")
        return problems

    def forbidden_findings(self) -> list[str]:
        found = []
        for p in self.editable_files():
            text = p.read_text(encoding="utf-8", errors="replace")
            for pat in self.forbidden:
                if pat in text:
                    line = text[: text.index(pat)].count("\n") + 1
                    found.append(f"{self.rel(p)}:{line}: forbidden construct `{pat}`")
            for match in re.finditer(r'\bextern\s*(?:"C(?:-unwind)?"\s*)?\{|\blibc\s*::|#\s*\[\s*link\s*\(', text):
                line = text[:match.start()].count("\n") + 1
                found.append(f"{self.rel(p)}:{line}: forbidden foreign-code construct `{match.group(0)}`")
        return found

    def interface_findings(self) -> list[str]:
        """Declared items of every `src/interfaces/<module>.rs` that `src/<module>.rs` does not provide unchanged."""
        found: list[str] = []
        idir = self.crate / "src" / "interfaces"
        if not idir.exists():
            return found
        for spec in sorted(idir.glob("*.rs")):
            impl = self.crate / "src" / spec.name
            if not impl.exists():
                found.append(f"src/{spec.name}: missing file (interface `src/interfaces/{spec.name}` has no implementation module)")
                continue
            try:
                found.extend(interface_check.check_module(spec.read_text(encoding="utf-8", errors="replace"),
                                                          impl.read_text(encoding="utf-8", errors="replace"), spec.stem))
            except Exception as exc:  # the checker must never stop a run
                found.append(f"(interface checker could not analyse src/{spec.name}: {exc})")
        return found

    def stub_findings(self) -> list[str]:
        """Bodies the agent has not translated yet (`unimplemented!()` / `todo!()` left over from the interface stubs).
        Tests may not exercise every module, so a green test run alone does not mean the project is fully translated."""
        found = []
        for p in self.editable_files():
            for no, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if re.search(r"\b(?:unimplemented|todo)!\s*[(\[{]", line) and not line.lstrip().startswith("//"):
                    found.append(f"{self.rel(p)}:{no}: {line.strip()[:100]}")
        return found

    # ----- agent actions
    def write_file(self, rel: str, content: str) -> str | None:
        """Returns an error message or None on success."""
        rel = rel.strip()
        if rel.startswith("./"):
            rel = rel[2:]
        if not self.is_editable(rel):
            return f"refused: `{rel}` is not an editable path (editable: src/*.rs; protected: {', '.join(self.protected_patterns)})"
        target = self.crate / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        safe_write(target, content if content.endswith("\n") else content + "\n")
        return None

    def append_file(self, rel: str, content: str) -> str | None:
        """Append to a file (used to continue a file whose reply was cut off by the output limit)."""
        rel = rel.strip()
        if rel.startswith("./"):
            rel = rel[2:]
        if not self.is_editable(rel):
            return f"refused: `{rel}` is not an editable path"
        target = self.crate / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        if existing and not existing.endswith("\n"):
            existing += "\n"
        safe_write(target, existing + (content if content.endswith("\n") else content + "\n"))
        return None

    def edit_file(self, rel: str, search: str, replace: str) -> str | None:
        rel = rel.strip()
        if rel.startswith("./"):
            rel = rel[2:]
        if not self.is_editable(rel):
            return f"refused: `{rel}` is not an editable path"
        target = self.crate / rel
        if not target.exists():
            return f"edit failed: `{rel}` does not exist"
        text = target.read_text(encoding="utf-8")
        count = text.count(search)
        if count == 0:
            return f"edit failed in `{rel}`: search text not found (it must match the current file exactly)"
        if count > 1:
            return f"edit failed in `{rel}`: search text occurs {count} times (make it unique)"
        safe_write(target, text.replace(search, replace, 1))
        return None

    def read_file(self, rel: str, max_chars: int = 60000) -> str:
        """Read from crate (src/..., Cargo.toml) or from the subject's original C sources (c_source/...)."""
        rel = rel.strip().lstrip("/")
        if ".." in rel.split("/"):
            return "error: path escapes the project"
        if rel.startswith("c_source/"):
            path = self.subject / rel
        else:
            path = self.crate / rel
        if not path.is_file():
            return f"error: file not found: {rel}"
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + f"\n... [truncated, {len(text) - max_chars} more characters]"
        return text

    def tree(self) -> str:
        lines = []
        for base, label in ((self.crate, "crate (editable area: src/*.rs)"), (self.subject / "c_source", "c_source (read-only original C project)")):
            lines.append(f"{label}:")
            if base.exists():
                for p in sorted(base.rglob("*")):
                    rel = p.relative_to(base)
                    if p.is_file() and not any(part in ("target", ".git") for part in rel.parts):
                        prefix = "c_source/" if "c_source" in label else ""
                        lines.append(f"  {prefix}{str(rel).replace(chr(92), '/')}  ({p.stat().st_size} bytes)")
        return "\n".join(lines)


# ----------------------------------------------------------------------------- reply parsing
FILE_RE = re.compile(r'<file\s+path="([^"]+)"\s*>\n?(.*?)\n?</file>', re.S)
EDIT_RE = re.compile(
    r'<edit\s+path="([^"]+)"\s*>\s*<search>\n?(.*?)\n?</search>\s*<replace>\n?(.*?)\n?</replace>(?:\s*</edit>)?', re.S
)  # the closing </edit> is optional: models often forget it, and everything else is unambiguous
EDIT_START_RE = re.compile(r'<edit\s+path="([^"]+)"')
READ_RE = re.compile(r'<read\s+path="([^"]+)"\s*/?>')
NOTES_RE = re.compile(r"<notes>\n?(.*?)\n?</notes>", re.S)
DONE_RE = re.compile(r"<done\s*/?>")


def strip_fences(content: str) -> str:
    """Models sometimes wrap file bodies in a markdown fence or CDATA even when told not to."""
    text = content.strip("\n")
    stripped = text.strip()
    if stripped.startswith("<![CDATA["):
        stripped = stripped[len("<![CDATA["):]
        if stripped.endswith("]]>"):
            stripped = stripped[:-3]
        text = stripped
    m = re.match(r"^\s*```[a-zA-Z]*\n(.*?)\n```\s*$", text, re.S)
    return m.group(1) if m else text


BLOCK_START_RE = re.compile(r'<(file|append)\s+path="([^"]+)"\s*>')
BLOCK_END_RE = re.compile(
    r'</(?:file|append|edit)>\s*(?:]]>)?|<file\s+path=|<append\s+path=|<edit\s+path=|<notes>|<done\s*/?>'
)


def parse_reply(text: str) -> dict:
    """Parse the model reply into ordered operations plus a possibly cut-off trailing block.

    Tolerant by design (free models are sloppy): a <file>/<append> block ends at any closing
    block tag, at the start of the next block, or at the end of the reply; CDATA/fence wrappers
    are stripped. A block that runs to the end of the reply without a closer is reported as
    `truncated` -- the caller accepts it as a complete block when the reply finished normally
    and treats it as a cut-off partial when the output limit was hit.

    ops: list of ("file"|"append", path, content) or ("edit", path, (search, replace)) in reply order.
    truncated: (kind, path, content_so_far) or None.
    """
    ops = []
    starts = list(BLOCK_START_RE.finditer(text))
    truncated = None
    for i, m in enumerate(starts):
        end = BLOCK_END_RE.search(text, m.end())
        content = text[m.end(): end.start() if end else len(text)]
        if end is None or (i == len(starts) - 1 and end.start() == len(text)):
            truncated = (m.group(1), m.group(2), content)
        else:
            ops.append((m.start(), m.group(1), m.group(2), strip_fences(content)))
    for m in EDIT_RE.finditer(text):
        ops.append((m.start(), "edit", m.group(1), (strip_fences(m.group(2)), strip_fences(m.group(3)))))
    ops.sort(key=lambda o: o[0])
    parsed_edits = len(EDIT_RE.findall(text))
    malformed_edits = max(0, len(EDIT_START_RE.findall(text)) - parsed_edits)
    return {
        "malformed_edits": malformed_edits,
        "ops": [o[1:] for o in ops],
        "truncated": truncated,
        "reads": READ_RE.findall(text),
        "notes": (NOTES_RE.findall(text) or [None])[-1],
        "done": bool(DONE_RE.search(text)),
    }


def salvage_partial(content: str) -> tuple[str, int, str]:
    """Cut a truncated block back to its last complete line. Returns (content, line_count, last_line)."""
    content = re.sub(r"^```[a-zA-Z]*\n", "", content)  # leading fence, if the model used one
    content = re.sub(r"^\s*<!\[CDATA\[", "", content)  # leading CDATA marker, if the model used one
    cut_at = content.rfind("\n")
    kept = content[: cut_at + 1] if cut_at != -1 else ""
    lines = kept.splitlines()
    return kept, len(lines), (lines[-1].strip()[:120] if lines else "")


# ----------------------------------------------------------------------------- redaction
def redact(text: str, secrets: list[str]) -> str:
    for s in secrets:
        if s and len(s) >= 8:
            text = text.replace(s, "[REDACTED]")
    text = re.sub(r"\bsk-[A-Za-z0-9_\-]{16,}", "[REDACTED]", text)
    text = re.sub(r"\bghp_[A-Za-z0-9]{20,}", "[REDACTED]", text)
    text = re.sub(r"(?i)(authorization:\s*bearer\s+)\S+", r"\1[REDACTED]", text)
    return text
