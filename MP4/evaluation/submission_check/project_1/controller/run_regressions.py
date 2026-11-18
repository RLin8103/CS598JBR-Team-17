#!/usr/bin/env python3
"""Run separate Rust regressions against the current translations and a sanitized C oracle."""
import argparse
import json
from pathlib import Path
import sys

from tools import cargo_env, run_cmd, sha256_file

MP4 = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--project-id", type=int, choices=[1, 2], help="filter extra tests to one project")
    args = ap.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = cargo_env(MP4 / ".runtime/target/regressions")
    # Executables/debug symbols are disposable, while textual evidence is retained.
    binaries = MP4 / ".runtime/oracles" / output.name
    binaries.mkdir(parents=True, exist_ok=True)
    oracle = binaries / "cset_oracle"
    compile_cmd = ["cc", "-std=c11", "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-g",
                   str(MP4 / "evaluation/harness/cset_oracle.c"), "-o", str(oracle)]
    compile_res = run_cmd(compile_cmd, MP4, env, 60)
    result = {"c_compile": compile_res, "source_sha256": {p.relative_to(MP4).as_posix(): sha256_file(p)
               for n in [1, 2] for p in (MP4 / f"translations/project_{n}/src").rglob("*.rs")}}
    csrc = MP4 / "subjects/project_2/c_source"
    psbt_oracle = binaries / "psbt_oracle"
    result["psbt_c_compile"] = run_cmd(["cc", "-std=c11", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
        "-I", str(MP4 / "evaluation/harness/compat"), str(MP4 / "evaluation/harness/psbt_oracle.c"),
        *[str(csrc / name) for name in ("psbt.c", "base64.c", "compactsize.c", "tx.c")], "-o", str(psbt_oracle)], MP4, env, 60)
    if result["psbt_c_compile"]["returncode"] == 0:
        result["psbt_c_oracle"] = run_cmd([str(psbt_oracle)], MP4, env, 30)
    if compile_res["returncode"] == 0:
        run = run_cmd([str(oracle)], MP4, env, 30)
        result["c_oracle"] = run
        if run["returncode"] == 0 and not run["timed_out"]:
            data = output / "cset_oracle.txt"
            data.write_text(run["stdout"])
            env["MP4_CSET_ORACLE"] = str(data)
            cmd = ["cargo", "+nightly-2025-05-13", "test", "--offline", "--locked", "--manifest-path",
                   str(MP4 / "evaluation/harness/Cargo.toml")]
            if args.project_id == 1:
                cmd += ["cset_"]
            cmd += ["--", "--test-threads=1"]
            if args.project_id == 2:
                cmd += ["--skip", "cset_"]
            result["rust"] = run_cmd(cmd, MP4, env, 300)
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    rust = result.get("rust", {})
    print(rust.get("stdout", "") + rust.get("stderr", ""))
    if "rust" not in result:
        print(json.dumps(result, indent=2))
    c_ok = all(result.get(key, {}).get("returncode") == 0 and not result.get(key, {}).get("timed_out", True)
               for key in ("c_compile", "c_oracle", "psbt_c_compile", "psbt_c_oracle"))
    return 0 if c_ok and rust.get("returncode") == 0 and not rust.get("timed_out", True) else 1


if __name__ == "__main__":
    sys.exit(main())
