#!/usr/bin/env python3
"""Load an ignored local key into this process's environment, then run a controller script.

The controller still obtains credentials only from its environment. The key never
appears in argv, a log, or a generated configuration. This helper makes no API calls.
"""
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys

MP4 = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: with_key.py SCRIPT [SCRIPT_ARGUMENTS...]")
    key_file = MP4 / "API_KEY.txt"
    if subprocess.run(["git", "check-ignore", "-q", "--", str(key_file)], cwd=MP4).returncode != 0:
        raise SystemExit("Credential file must be ignored by Git before it can be used")
    if subprocess.run(["git", "ls-files", "--error-unmatch", str(key_file)], cwd=MP4,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        raise SystemExit("Refusing to use a tracked credential file")
    key = key_file.read_text().strip()
    if key.startswith("export "):
        key = key[7:].strip()
    if "=" in key and key.split("=", 1)[0].strip() == "OPENROUTER_API_KEY":
        key = key.split("=", 1)[1].strip()
    key = key.strip("\"'")
    if not re.fullmatch(r"sk-or-v1-[A-Za-z0-9_-]+", key):
        raise SystemExit("Unrecognized credential format; contents were not displayed")
    script = Path(sys.argv[1]).resolve()
    if not script.is_relative_to(MP4 / "src") or not script.is_file():
        raise SystemExit("Target must be a script inside MP4/src")
    os.environ["OPENROUTER_API_KEY"] = key
    sys.argv = [str(script), *sys.argv[2:]]
    sys.path.insert(0, str(script.parent))
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
