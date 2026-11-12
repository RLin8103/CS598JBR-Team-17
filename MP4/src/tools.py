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

HERE = Path(__file__).resolve().parent


# ----------------------------------------------------------------------------- process runner
def run_cmd(cmd: list[str], cwd: Path, env: dict, timeout: int) -> dict:
    started = time.time()
    proc = subprocess.Popen(
        cmd, cwd=str(cwd), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors="replace", start_new_session=True,
    )
    timed_out = False
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
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
    }


def cargo_env(target_dir: Path) -> dict:
    env = os.environ.copy()
    cargo_bin = str(Path.home() / ".cargo" / "bin")
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
        res["ok"] = res["returncode"] == 0
        res["error_count"] = len(errors)
        res["warning_count"] = sum(1 for l in res["stderr"].splitlines() if l.startswith("warning:") and "generated" not in l)
        res["pretty"] = "" if res["ok"] else res["stderr"]
        return res

    # ------------------------------------------------------------------ tests
    def test(self) -> dict:
        res = self._cargo("test", "--no-fail-fast", timeout=self.test_timeout)
        text = res["stdout"] + "\n" + res["stderr"]
        passed = failed = ignored = 0
        for m in re.finditer(r"test result: \w+\. (\d+) passed; (\d+) failed; (\d+) ignored", text):
            passed += int(m.group(1))
            failed += int(m.group(2))
            ignored += int(m.group(3))
        failing = sorted(set(re.findall(r"^test (\S+) \.\.\. FAILED", text, re.M)))
        passing = sorted(set(re.findall(r"^test (\S+) \.\.\. ok", text, re.M)))
        res.update({
            "passed": passed, "failed": failed, "ignored": ignored, "total": passed + failed,
            "failing_tests": failing, "passing_tests": passing,
            "compile_failed": ("could not compile" in text) and passed + failed == 0,
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
        for group in self.groups:
            self._touch_sources()  # make cargo re-run clippy with different lint flags
            res = self._cargo(
                "clippy", *self.clippy_extra, "--message-format=json", "--", "-A", "clippy::all", "-W", f"clippy::{group}"
            )
            seen = set()
            msgs: list[str] = []
            for line in res["stdout"].splitlines():
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("reason") != "compiler-message":
                    continue
                m = obj["message"]
                code = (m.get("code") or {}).get("code") or ""
                if not code.startswith("clippy::") or m.get("level") not in ("warning", "error"):
                    continue
                text = m.get("rendered") or m.get("message", "")
                if text in seen:
                    continue
                seen.add(text)
                msgs.append(text.strip())
            counts[group] = len(msgs)
            rendered[group] = msgs
            raw_logs[group] = res["stderr"][-3000:]
        compile_failed = any("could not compile" in raw_logs[g] and counts[g] == 0 for g in self.groups)
        return {
            "counts": counts, "total": sum(counts.values()), "rendered": rendered,
            "compile_failed": compile_failed, "raw_stderr_tail": raw_logs,
        }

    # ------------------------------------------------------------------ safety
    def unsafe_metrics(self) -> dict:
        command = self.cfg["unsafe_metrics"].get("command")
        if command:
            cmd = shlex.split(command.replace("{path}", str(self.crate)))
            res = run_cmd(cmd, self.crate, self.env, self.cmd_timeout)
            try:
                data = json.loads(res["stdout"])
                totals = data.get("totals", data)
                return {"tool": "official", "totals": totals, "offenders": data.get("offenders", []), "raw": res["stdout"][-4000:]}
            except json.JSONDecodeError:
                return {"tool": "official", "totals": {}, "offenders": [], "raw": (res["stdout"] + res["stderr"])[-4000:],
                        "error": "official unsafe-metrics output was not JSON; see raw"}
        sys.path.insert(0, str(HERE))
        import unsafe_check  # noqa: WPS433 (local import keeps the module optional)
        return unsafe_check.analyse(self.crate)


PRIMARY = ("unsafe_lines", "unsafe_calls", "unsafe_casts", "pointer_arithmetic")


def unsafe_primary_total(metrics: dict) -> int:
    totals = metrics.get("totals", {})
    return sum(int(totals.get(k, 0) or 0) for k in PRIMARY)


# ----------------------------------------------------------------------------- guarded workspace
def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def glob_match(rel: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        return rel.startswith(pattern[:-3] + "/")
    return fnmatch.fnmatch(rel, pattern)


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
        if self.is_protected(rel) or ".." in rel.split("/") or rel.startswith("/"):
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
        self.protected_hashes = {}
        for p in sorted(self.crate.rglob("*")):
            if p.is_file() and "target" not in p.relative_to(self.crate).parts:
                rel = self.rel(p)
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
        for p in (self.crate / "src").rglob("*"):
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
        target.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")
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
        target.write_text(existing + (content if content.endswith("\n") else content + "\n"), encoding="utf-8")
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
        target.write_text(text.replace(search, replace, 1), encoding="utf-8")
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
    r'<edit\s+path="([^"]+)"\s*>\s*<search>\n?(.*?)\n?</search>\s*<replace>\n?(.*?)\n?</replace>\s*</edit>', re.S
)
READ_RE = re.compile(r'<read\s+path="([^"]+)"\s*/?>')
NOTES_RE = re.compile(r"<notes>\n?(.*?)\n?</notes>", re.S)
DONE_RE = re.compile(r"<done\s*/?>")


def strip_fences(content: str) -> str:
    """Models sometimes wrap file bodies in a markdown fence even when told not to."""
    m = re.match(r"^\s*```[a-zA-Z]*\n(.*?)\n```\s*$", content, re.S)
    return m.group(1) if m else content


APPEND_RE = re.compile(r'<append\s+path="([^"]+)"\s*>\n?(.*?)\n?</append>', re.S)
OPEN_RE = re.compile(r'<(file|append)\s+path="([^"]+)"\s*>\n?')


def parse_reply(text: str) -> dict:
    """Parse the model reply into ordered operations plus a possibly cut-off trailing block.

    ops: list of ("file"|"append", path, content) or ("edit", path, (search, replace)) in reply order.
    truncated: (kind, path, content_so_far) when the reply ended inside an unclosed <file>/<append>
    block (typically because the output-token limit was hit), else None.
    """
    ops = []
    for m in FILE_RE.finditer(text):
        ops.append((m.start(), "file", m.group(1), strip_fences(m.group(2))))
    for m in APPEND_RE.finditer(text):
        ops.append((m.start(), "append", m.group(1), strip_fences(m.group(2))))
    for m in EDIT_RE.finditer(text):
        ops.append((m.start(), "edit", m.group(1), (strip_fences(m.group(2)), strip_fences(m.group(3)))))
    ops.sort(key=lambda o: o[0])

    truncated = None
    opens = list(OPEN_RE.finditer(text))
    if opens:
        last = opens[-1]
        if f"</{last.group(1)}>" not in text[last.end():]:
            truncated = (last.group(1), last.group(2), text[last.end():])
    return {
        "ops": [o[1:] for o in ops],
        "truncated": truncated,
        "reads": READ_RE.findall(text),
        "notes": (NOTES_RE.findall(text) or [None])[-1],
        "done": bool(DONE_RE.search(text)),
    }


def salvage_partial(content: str) -> tuple[str, int, str]:
    """Cut a truncated block back to its last complete line. Returns (content, line_count, last_line)."""
    content = re.sub(r"^```[a-zA-Z]*\n", "", content)  # leading fence, if the model used one
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
