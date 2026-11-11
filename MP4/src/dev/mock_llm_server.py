#!/usr/bin/env python3
"""Scripted fake LLM endpoint used ONLY to smoke-test the controller plumbing offline.

It is not used to produce any submitted translation. It replays a tiny fixed script:
  call 1: asks to read a C file            (exercises <read>)
  call 2: one good edit, one bad edit, one write to a protected file, notes (exercises guards)
  call 3+: <done/>
Usage: python3 mock_llm_server.py [port]
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

CALLS = {"n": 0}

SCRIPT = [
    '<read path="c_source/src/cset.h"/>',
    '''Plan: implement the endianness probe first.
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
</notes>''',
]


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        i = CALLS["n"]
        CALLS["n"] += 1
        content = SCRIPT[i] if i < len(SCRIPT) else "Nothing more to do. <done/>"
        resp = {
            "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
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
