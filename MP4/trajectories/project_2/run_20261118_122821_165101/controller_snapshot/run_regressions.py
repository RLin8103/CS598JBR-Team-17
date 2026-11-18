#!/usr/bin/env python3
"""Run the separate Rust regression suite and the assigned project's C oracle."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

from regression_results import named_outcomes, source_hashes
from tools import cargo_env, process_ok, run_cmd

MP4 = Path(__file__).resolve().parent.parent
HARNESS = MP4 / "evaluation/harness"


def evaluate(project_id, output, binaries):
    env = cargo_env(MP4 / ".runtime/target/regressions")
    crates = {str(n): MP4 / f"translations/project_{n}" for n in (1, 2)}
    result = {"project_id": project_id, "source_sha256": {key: source_hashes(crate) for key, crate in crates.items()}}
    csrc = MP4 / "subjects/project_2/c_source"
    oracle = binaries / "oracle"
    args = [str(HARNESS / "cset_oracle.c")] if project_id == 1 else [
        "-I", str(HARNESS / "compat"), str(HARNESS / "psbt_oracle.c"),
        *[str(csrc / name) for name in ("psbt.c", "base64.c", "compactsize.c", "tx.c")],
    ]
    result["c_compile"] = run_cmd(["cc", "-std=c11", "-fsanitize=address,undefined",
                                  "-fno-sanitize-recover=all", "-g", *args, "-o", str(oracle)], MP4, env, 60)
    if not process_ok(result["c_compile"]):
        return result
    result["c_oracle"] = run_cmd([str(oracle)], MP4, env, 30)
    if not process_ok(result["c_oracle"]):
        return result
    if project_id == 1:
        data = output / "cset_oracle.txt"
        data.write_text(result["c_oracle"]["stdout"])
        env["MP4_CSET_ORACLE"] = str(data)
    cmd = ["cargo", "+nightly-2025-05-13", "test", "--offline", "--locked", "--lib",
           "--manifest-path", str(HARNESS / "Cargo.toml")]
    cmd += ["cset_", "--"] if project_id == 1 else ["--", "--skip", "cset_"]
    result["inventory"] = run_cmd([*cmd, "--list"], MP4, env, 300)
    if process_ok(result["inventory"]):
        result["rust"] = run_cmd([*cmd, "--test-threads=1"], MP4, env, 300)
        try:
            result["outcomes"] = named_outcomes(result["inventory"], result["rust"])
        except ValueError as error:
            result["error"] = str(error)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--project-id", type=int, choices=[1, 2])
    args = ap.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.project_id is None:
        return max(run_project(n, output / f"project_{n}") for n in (1, 2))
    return run_project(args.project_id, output)


def run_project(project_id, output):
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mp4-oracle-") as binaries:
        result = evaluate(project_id, output, Path(binaries))
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    last = next(result[key] for key in ("rust", "inventory", "c_oracle", "c_compile") if key in result)
    print(last["stdout"] + last["stderr"])
    if result.get("error"):
        print(result["error"])
    outcomes = result.get("outcomes")
    return int(not outcomes or any(value != "ok" for value in outcomes.values()))


if __name__ == "__main__":
    sys.exit(main())
