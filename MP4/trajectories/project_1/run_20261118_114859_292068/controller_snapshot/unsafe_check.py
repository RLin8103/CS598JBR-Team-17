#!/usr/bin/env python3
"""Built-in approximation of the unsafe-metrics analyzer (standard library only).

The instructional team provides the official unsafe-metrics tool. Until that tool is
configured (`unsafe_metrics.command` in configs/pipeline.json) the pipeline uses this
lexical approximation so the agent still receives safety feedback in every iteration.
It analyses generated code only (src/**/*.rs, excluding src/bin and src/interfaces).

Metrics (same names as the assignment):
  unsafe_lines      non-empty, non-comment lines inside `unsafe {}` blocks / `unsafe fn` bodies
  unsafe_calls      calls to unsafe functions (known unsafe std APIs, crate `unsafe fn`s, FFI)
  unsafe_casts      `as *const T`, `as *mut T`, transmute
  pointer_arithmetic  ptr.add/sub/offset/byte_* and equivalents
Extra: unsafe_blocks, unsafe_fns, raw_pointer_decls, ffi_calls, transmute_uses,
       manual_alloc_ops, forbid_unsafe_files.

Usage: python3 unsafe_check.py <crate_root> [--json]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

UNSAFE_CALLEES = {
    "from_raw_parts", "from_raw_parts_mut", "from_utf8_unchecked", "from_utf8_unchecked_mut",
    "get_unchecked", "get_unchecked_mut", "transmute", "transmute_copy", "read", "write",
    "read_unaligned", "write_unaligned", "read_volatile", "write_volatile", "copy",
    "copy_nonoverlapping", "write_bytes", "offset_from", "alloc", "dealloc", "realloc",
    "alloc_zeroed", "malloc", "calloc", "free", "memcpy", "memmove", "memset", "memcmp",
    "strlen", "strcmp", "strcpy", "from_raw", "unwrap_unchecked", "assume_init", "zeroed",
    "uninitialized", "set_len", "drop_in_place", "as_ref_unchecked", "unreachable_unchecked",
    "get_unchecked_mut", "add", "sub", "offset", "byte_add", "byte_sub", "byte_offset",
}
PTR_ARITH = {
    "add", "sub", "offset", "byte_add", "byte_sub", "byte_offset", "wrapping_add",
    "wrapping_sub", "wrapping_offset", "offset_from", "byte_offset_from",
}
ALLOC_NAMES = {"alloc", "dealloc", "realloc", "alloc_zeroed", "malloc", "calloc", "free", "from_raw", "into_raw"}


def strip_code(src: str) -> str:
    """Blank out comments, string and char literals but keep every newline and column."""
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            while i < n and src[i] != "\n":
                out.append(" ")
                i += 1
        elif c == "/" and nxt == "*":
            depth = 0
            while i < n:
                if src.startswith("/*", i):
                    depth += 1
                    out.append("  ")
                    i += 2
                elif src.startswith("*/", i):
                    depth -= 1
                    out.append("  ")
                    i += 2
                    if depth == 0:
                        break
                else:
                    out.append("\n" if src[i] == "\n" else " ")
                    i += 1
        elif c == "r" and re.match(r'r#*"', src[i:i + 10] or ""):
            m = re.match(r'r(#*)"', src[i:])
            hashes = m.group(1)
            end = '"' + hashes
            j = src.find(end, i + len(m.group(0)))
            j = n if j == -1 else j + len(end)
            out.append("".join("\n" if ch == "\n" else " " for ch in src[i:j]))
            i = j
        elif c == '"':
            out.append('"')
            i += 1
            while i < n and src[i] != '"':
                if src[i] == "\\" and i + 1 < n:
                    out.append(" ")
                    i += 1
                out.append("\n" if src[i] == "\n" else " ")
                i += 1
            out.append('"')
            i += 1
        elif c == "'":
            m = re.match(r"'(\\.[^']*|[^\\'])'", src[i:i + 12])
            if m:
                out.append("'" + " " * (len(m.group(0)) - 2) + "'")
                i += len(m.group(0))
            else:
                out.append(c)
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def match_brace(code: str, open_idx: int) -> int:
    depth = 0
    for i in range(open_idx, len(code)):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(code) - 1


def line_of(code: str, idx: int) -> int:
    return code.count("\n", 0, idx) + 1


def analyse_file(path: Path, root: Path, crate_unsafe_fns: set[str]) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    code = strip_code(raw)
    raw_lines = raw.split("\n")
    code_lines = code.split("\n")
    rel = str(path.relative_to(root)).replace("\\", "/")

    ranges: list[tuple[int, int]] = []  # (start_idx, end_idx) of unsafe regions
    blocks = fns = 0
    for m in re.finditer(r"\bunsafe\b", code):
        tail = code[m.end():m.end() + 200]
        if re.match(r"\s*\{", tail):
            open_idx = m.end() + tail.index("{")
            ranges.append((m.start(), match_brace(code, open_idx)))
            blocks += 1
        elif re.match(r"\s*(extern\s*(\"[^\"]*\"\s*)?)?fn\b", tail):
            brace = code.find("{", m.end())
            semi = code.find(";", m.end())
            if brace != -1 and (semi == -1 or brace < semi):
                ranges.append((m.start(), match_brace(code, brace)))
            fns += 1
        elif re.match(r"\s*(impl|trait)\b", tail):
            brace = code.find("{", m.end())
            if brace != -1:
                ranges.append((m.start(), match_brace(code, brace)))
            fns += 1  # counted as an unsafe declaration
    for m in re.finditer(r'\bextern\s*"[^"]*"\s*\{', code):
        ranges.append((m.start(), match_brace(code, m.end() - 1)))

    unsafe_line_numbers: set[int] = set()
    for a, b in ranges:
        la, lb = line_of(code, a), line_of(code, b)
        for ln in range(la, lb + 1):
            if code_lines[ln - 1].strip():
                unsafe_line_numbers.add(ln)

    def in_unsafe(idx: int) -> bool:
        return any(a <= idx <= b for a, b in ranges)

    calls, casts, arith, ffi, transmutes, allocs, raw_decls = [], [], [], [], [], [], []
    for m in re.finditer(r"\bas\s+\*\s*(const|mut)\b", code):
        casts.append(line_of(code, m.start()))
    for m in re.finditer(r"\btransmute(_copy)?\b", code):
        casts.append(line_of(code, m.start()))
        transmutes.append(line_of(code, m.start()))
    for m in re.finditer(r"\*\s*(const|mut)\s+[A-Za-z_(\[]", code):
        if not re.search(r"\bas\s*$", code[max(0, m.start() - 4):m.start()]):
            raw_decls.append(line_of(code, m.start()))
    for m in re.finditer(r"(?:(\w+(?:::\w+)*)|\.(\w+))\s*(?:::<[^>]*>)?\s*\(", code):
        name = (m.group(1) or m.group(2)).split("::")[-1]
        is_method = m.group(2) is not None
        idx = m.start()
        ln = line_of(code, idx)
        if is_method and name in PTR_ARITH and (in_unsafe(idx) or re.search(r"\*\s*(const|mut)", code_lines[ln - 1])):
            arith.append(ln)
        if name in ALLOC_NAMES and in_unsafe(idx):
            allocs.append(ln)
        if in_unsafe(idx):
            if name in crate_unsafe_fns or (name in UNSAFE_CALLEES and not (is_method and name in PTR_ARITH)):
                if code[max(0, idx - 3):idx] != "fn " and not re.search(r"\bfn\s+$", code[max(0, idx - 8):idx]):
                    calls.append(ln)
    for m in re.finditer(r'\bextern\s*"[^"]*"\s*\{([^}]*)\}', code):
        for f in re.finditer(r"\bfn\s+(\w+)", m.group(1)):
            ffi.append(line_of(code, m.start()))
    forbid = bool(re.search(r"#!\[forbid\(unsafe_code\)\]", code))

    return {
        "file": rel,
        "unsafe_line_numbers": sorted(unsafe_line_numbers),
        "unsafe_calls": calls,
        "unsafe_casts": casts,
        "pointer_arithmetic": arith,
        "unsafe_blocks": blocks,
        "unsafe_fns": fns,
        "raw_pointer_decls": raw_decls,
        "ffi_calls": ffi,
        "transmute_uses": transmutes,
        "manual_alloc_ops": allocs,
        "forbid": forbid,
        "_raw_lines": raw_lines,
    }


def crate_sources(root: Path) -> list[Path]:
    files = []
    for p in sorted((root / "src").rglob("*.rs")):
        rel = p.relative_to(root / "src").parts
        if rel and rel[0] in ("bin", "interfaces"):
            continue
        files.append(p)
    return files


def analyse(root: Path) -> dict:
    files = crate_sources(root)
    unsafe_fn_names: set[str] = set()
    for p in files:
        code = strip_code(p.read_text(encoding="utf-8", errors="replace"))
        for m in re.finditer(r"\bunsafe\s+(?:extern\s*(?:\"[^\"]*\"\s*)?)?fn\s+(\w+)", code):
            unsafe_fn_names.add(m.group(1))
    per_file = [analyse_file(p, root, unsafe_fn_names) for p in files]
    totals = {
        "unsafe_lines": sum(len(f["unsafe_line_numbers"]) for f in per_file),
        "unsafe_calls": sum(len(f["unsafe_calls"]) for f in per_file),
        "unsafe_casts": sum(len(f["unsafe_casts"]) for f in per_file),
        "pointer_arithmetic": sum(len(f["pointer_arithmetic"]) for f in per_file),
        "unsafe_blocks": sum(f["unsafe_blocks"] for f in per_file),
        "unsafe_fns": sum(f["unsafe_fns"] for f in per_file),
        "raw_pointer_decls": sum(len(f["raw_pointer_decls"]) for f in per_file),
        "ffi_calls": sum(len(f["ffi_calls"]) for f in per_file),
        "transmute_uses": sum(len(f["transmute_uses"]) for f in per_file),
        "manual_alloc_ops": sum(len(f["manual_alloc_ops"]) for f in per_file),
        "files_with_forbid_unsafe_code": sum(1 for f in per_file if f["forbid"]),
        "files_analysed": len(per_file),
    }
    offenders = []
    for f in per_file:
        lines = f["_raw_lines"]
        seen: set[int] = set()
        for key in ("unsafe_calls", "unsafe_casts", "pointer_arithmetic", "raw_pointer_decls", "ffi_calls"):
            for ln in f[key]:
                if ln not in seen:
                    seen.add(ln)
                    offenders.append({"file": f["file"], "line": ln, "kind": key, "text": lines[ln - 1].strip()[:160]})
        for ln in f["unsafe_line_numbers"]:
            if ln not in seen and len(offenders) < 400:
                seen.add(ln)
                offenders.append({"file": f["file"], "line": ln, "kind": "unsafe_line", "text": lines[ln - 1].strip()[:160]})
    offenders.sort(key=lambda o: (o["file"], o["line"]))
    return {"tool": "builtin-approximation", "totals": totals, "offenders": offenders[:120]}


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    result = analyse(Path(argv[1]).resolve())
    if "--json" in argv:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result["totals"].items():
            print(f"{k:32s} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
