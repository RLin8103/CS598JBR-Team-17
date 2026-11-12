#!/usr/bin/env python3
"""Scripted fake LLM endpoint used ONLY to smoke-test the controller plumbing offline.

It is not used to produce any submitted translation. It replays a tiny fixed script:
  call 1: asks to read a C file                                   (exercises <read>)
  call 2: one good edit, one bad edit, a write to a protected file (exercises edit + guard rails)
  call 3: a <file> block cut off by the output limit               (exercises partial-save)
  call 4: <append> that finishes the file                          (exercises continuation)
  call 5+: <done/>
Usage: python3 mock_llm_server.py [port]
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

CALLS = {"n": 0}

# (content, finish_reason)
SCRIPT = [
    ('<read path="c_source/src/cset.h"/>', "stop"),
    ('''Plan: implement the endianness probe first.
<edit path="src/cset.rs">
<search>
pub fn xxh_is_little_endian() -> bool {
    unimplemented!()
}
</search>
<replace>
pub fn xxh_is_little_endian() -> bool {
    cfg!(target_endian = "little")
}
</replace>
</edit>
<edit path="src/cset.rs">
<search>
this text does not exist
</search>
<replace>
x
</replace>
</edit>
<file path="src/lib.rs">
pub mod hacked;
</file>
<notes>
done: xxh_is_little_endian. todo: everything else.
</notes>''', "stop"),
    ('''Rewriting the whole file.
<file path="src/cset.rs">
pub type XXH64HashT = u64;
pub type XXHU8 = u8;
pub fn xxh_is_litt''', "length"),
    ('''<append path="src/cset.rs">
pub fn xxh_is_little_endian() -> bool {
    cfg!(target_endian = "little")
}
</append>
<notes>
file finished after the cut-off.
</notes>''', "stop"),
]


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        i = CALLS["n"]
        CALLS["n"] += 1
        content, finish = SCRIPT[i] if i < len(SCRIPT) else ("Nothing more to do. <done/>", "stop")
        resp = {
            "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": finish}],
            "usage": {"prompt_tokens": sum(len(m["content"]) for m in body["messages"]) // 4, "completion_tokens": len(content) // 4},
        }
        data = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
