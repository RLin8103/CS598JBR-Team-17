#!/usr/bin/env python3
"""Interface-conformance check (standard library only).

The CRUST-Bench interface files (`src/interfaces/<module>.rs`) are part of the specification: hidden tests are
compiled against them. The agent receives them as stubs and implements `src/<module>.rs`, but nothing stops it
from "improving" a signature (different parameter types, `&self` instead of `&mut self`, extra trait bounds on an
`impl<T>` header, changed struct fields, a missing function). This module compares the items declared in an
interface file with the implementation file and returns human-readable findings that the controller feeds back to
the model. Only the *declared* items are checked: extra private helpers, extra impl blocks and extra derives are fine.

Checked: free functions (any visibility), `pub fn` inside impl blocks (keyed by the impl header), struct / enum
definitions (field and variant lists), `const` / `static` types and `type` aliases, and the impl headers themselves
(so `impl<T> Cset<T>` cannot silently become `impl<T: Hash> Cset<T>`).
"""
from __future__ import annotations

import re


# ----------------------------------------------------------------------------- lexical helpers
def strip_comments_and_attrs(text: str) -> str:
    out, i, n = [], 0, len(text)
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
        elif text.startswith("/*", i):
            depth = 1
            i += 2
            while i < n and depth:
                if text.startswith("/*", i):
                    depth += 1
                    i += 2
                elif text.startswith("*/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
        else:
            out.append(c)
            i += 1
    cleaned = "".join(out)
    return re.sub(r"#!?\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]", "", cleaned)


def squash(s: str) -> str:
    return re.sub(r"\s+", "", s)


def pretty(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def match_close(text: str, i: int, open_c: str, close_c: str) -> int:
    """Index of the bracket that closes the one at text[i] (string literals are skipped)."""
    depth, n, in_str = 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n - 1


def header_end(text: str, pos: int) -> tuple[int, str]:
    """Position and kind ('{' or ';' or '') of the first block-start / terminator outside (), [] and strings."""
    depth, n, in_str, i = 0, len(text), False, pos
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and c in "{;":
            return i, c
        i += 1
    return n, ""


def split_top_level(s: str, sep: str = ",") -> list[str]:
    parts, depth, cur = [], 0, []
    s = s.replace("->", "\u2192")
    for c in s:
        if c in "(<[{":
            depth += 1
        elif c in ")>]}":
            depth -= 1
        if c == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        parts.append("".join(cur))
    return [p.replace("\u2192", "->").strip() for p in parts]


# ----------------------------------------------------------------------------- item parsing
FN_RE = re.compile(r"^(?P<vis>pub(?:\([^)]*\))?\s+)?(?:(?:const|async|unsafe|extern\s+\"[^\"]*\")\s+)*fn\s+(?P<name>\w+)")


def parse_fn(header: str, self_ty: str = "") -> tuple[str, str, str] | None:
    """Returns (name, normalized signature, readable signature) for a `fn` header."""
    h = header.strip()
    m = FN_RE.match(h)
    if not m:
        return None
    name = m.group("name")
    rest = h[m.end():]
    generics = ""
    if rest.lstrip().startswith("<"):
        r = rest.lstrip()
        end = match_close(r.replace("->", "\u2192"), 0, "<", ">")
        generics = r[: end + 1]
        rest = r[end + 1:]
    rest = rest.lstrip()
    if not rest.startswith("("):
        return None
    close = match_close(rest, 0, "(", ")")
    raw_params = rest[1:close]
    tail = rest[close + 1:]
    params = []
    for p in split_top_level(raw_params):
        if ":" in p.replace("::", ""):
            ty = p.split(":", 1)[1] if not p.lstrip().startswith(("&", "self", "mut self")) else p
            params.append(squash(ty))
        else:  # receiver: self, &self, &mut self, mut self
            params.append(squash(re.sub(r"^mut\s+self$", "self", p.strip())))
    ret = "()"
    ret_shown = "()"
    where = ""
    tm = re.match(r"\s*->\s*(.*)$", tail, re.S)
    if tm:
        ret_and_where = tm.group(1)
        wm = re.search(r"\bwhere\b", ret_and_where)
        ret_shown = pretty(ret_and_where[: wm.start()] if wm else ret_and_where)
        ret = squash(ret_and_where[: wm.start()] if wm else ret_and_where)
        where = squash(ret_and_where[wm.start():]) if wm else ""
    else:
        wm = re.search(r"\bwhere\b", tail)
        where = squash(tail[wm.start():]) if wm else ""
    if self_ty:  # inside `impl X<T>` the type name and `Self` are the same type
        params = [p.replace(self_ty, "Self") for p in params]
        ret = ret.replace(self_ty, "Self")
    vis = "pub" if m.group("vis") else ""
    norm = f"{vis}|{squash(generics)}|({','.join(params)})->{ret}|{where}"
    shown = f"{'pub ' if vis else ''}fn {name}{pretty(generics)}({pretty(raw_params)}) -> {ret_shown}"
    return name, norm, shown


def parse_items(text: str, context: str = "", top: bool = True, self_ty: str = "") -> dict:
    """key -> (normalized signature, readable text)."""
    items: dict = {}
    pos, n = 0, len(text)
    while pos < n:
        while pos < n and text[pos].isspace():
            pos += 1
        if pos >= n:
            break
        end, kind = header_end(text, pos)
        header = text[pos:end]
        hs = header.strip()
        body = ""
        after = end + 1
        if kind == "{":
            close = match_close(text, end, "{", "}")
            body = text[end + 1: close]
            after = close + 1
        stripped = re.sub(r"^pub(?:\([^)]*\))?\s+", "", hs)
        fm = re.match(r"[A-Za-z_]+", stripped)
        first = fm.group(0) if fm else ""
        if first == "impl":
            hdr = pretty(hs)
            # Inherent impl blocks are identified by the type they extend (`Cset<T>`), so that a changed header
            # (extra bounds) is one finding instead of "every method is missing". Trait impls keep their full header.
            body_hdr = re.sub(r"^impl\s*", "", hdr)
            if body_hdr.startswith("<"):
                body_hdr = body_hdr[match_close(body_hdr.replace("->", "\u2192"), 0, "<", ">") + 1:].strip()
            body_hdr = re.split(r"\swhere\s", body_hdr)[0]
            ctx = squash(hdr) if re.search(r"\sfor\s", body_hdr) else squash(body_hdr)
            if " for " in f" {body_hdr} ":
                items[("impl", ctx)] = (squash(hdr), hdr, {squash(hdr)})
            else:
                prev = items.get(("impl", ctx))
                alts = (prev[2] if prev else set()) | {squash(hdr)}
                items[("impl", ctx)] = (squash(hdr), hdr, alts)
            items.update(parse_items(body, context=ctx, top=False, self_ty="" if " for " in f" {body_hdr} " else squash(body_hdr)))
        elif first in ("struct", "enum", "union"):
            name = re.match(r"(?:struct|enum|union)\s+(\w+)", stripped).group(1)
            full = hs + (" {" + body + "}" if kind == "{" else "")
            # `pub` on a field only widens visibility (harmless for the tests), so it is ignored in the comparison
            norm_full = re.sub(r"\bpub(?:\([^)]*\))?\s+", "", re.sub(r"^pub(?:\([^)]*\))?\s+", "", full.strip()))
            items[("type", name)] = (squash(norm_full), pretty(full)[:160])
        elif first in ("const", "static") and not stripped.startswith("const fn"):
            semi_end, _ = header_end(text, pos)
            # initialiser may contain braces: scan to ';' ignoring them
            j, depth, in_str = pos, 0, False
            while j < n:
                c = text[j]
                if in_str:
                    if c == "\\":
                        j += 2
                        continue
                    if c == '"':
                        in_str = False
                elif c == '"':
                    in_str = True
                elif c in "([{":
                    depth += 1
                elif c in ")]}":
                    depth -= 1
                elif c == ";" and depth == 0:
                    break
                j += 1
            decl = text[pos:j]
            lhs = decl.split("=", 1)[0]
            nm = re.search(r"(\w+)\s*:", lhs)
            items[("const", nm.group(1) if nm else pretty(lhs))] = (squash(lhs), pretty(lhs))
            after = j + 1
        elif first == "type":
            nm = re.match(r"type\s+(\w+)", stripped)
            j = text.find(";", pos)
            decl = text[pos: j if j != -1 else n]
            if nm:
                items[("alias", nm.group(1))] = (squash(decl), pretty(decl))
            after = (j if j != -1 else n) + 1
        else:
            f = parse_fn(hs, self_ty)
            if f and (top or hs.startswith("pub")):
                name, norm, shown = f
                items[("fn", context, name)] = (norm, shown)
        pos = max(after, end + 1)
    return items


# ----------------------------------------------------------------------------- public API
def check_module(interface_text: str, impl_text: str, module: str) -> list[str]:
    spec = parse_items(strip_comments_and_attrs(interface_text))
    got = parse_items(strip_comments_and_attrs(impl_text))
    findings: list[str] = []
    for key, val in spec.items():
        norm, shown = val[0], val[1]
        label = {"impl": "impl header", "type": "type", "const": "constant", "alias": "type alias", "fn": "function"}[key[0]]
        name = key[-1] if key[0] != "fn" else key[2]
        if key not in got:
            if key[0] == "impl":
                findings.append(f"src/{module}.rs: missing impl block required by the interface: `{shown}`")
            else:
                findings.append(f"src/{module}.rs: missing {label} required by the interface: `{shown}`")
        elif key[0] == "impl":
            if norm not in got[key][2]:
                findings.append(f"src/{module}.rs: {label} differs from the interface (do not add or remove generic bounds).\n"
                                f"      interface: `{shown}`\n      yours    : `{got[key][1]}`")
        elif got[key][0] != norm:
            findings.append(f"src/{module}.rs: {label} `{name}` differs from the interface.\n      interface: `{shown}`\n      yours    : `{got[key][1]}`")
    return findings
