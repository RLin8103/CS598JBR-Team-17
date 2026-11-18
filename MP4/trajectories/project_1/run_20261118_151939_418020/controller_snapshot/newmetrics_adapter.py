"""Run the course NewMetrics analyzer and return the library metrics as JSON."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from unsafe_check import analyse


def main():
    aggregate = Path(__file__).resolve().parents[1] / ".runtime/newmetrics/aggregate.py"
    if not aggregate.is_file():
        raise SystemExit(f"Install the course aggregate.py at {aggregate}")
    env = dict(os.environ, RUSTUP_TOOLCHAIN="nightly-2025-05-13")
    sysroot = subprocess.check_output(["rustc", "--print", "sysroot"], env=env, text=True).strip()
    if sys.platform == "darwin":
        env["DYLD_LIBRARY_PATH"] = str(Path(sysroot) / "lib")
    with tempfile.TemporaryDirectory(prefix="mp4-newmetrics-") as tmp:
        env["CARGO_TARGET_DIR"] = str(Path(tmp) / "target")
        crate = Path(tmp) / "crate"
        shutil.copytree(Path.cwd(), crate, ignore=shutil.ignore_patterns("target", ".git"))
        result = subprocess.run(["cargo", "newmetrics", "--offline"], env=env, cwd=crate,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(result.stdout, file=sys.stderr, end="")
        result.check_returncode()
        targets = re.split(r"(?m)^Target name: ", result.stdout)
        if len(targets) < 2 or not result.stdout.rstrip().endswith("cargo newmetrics finished"):
            raise SystemExit("Incomplete NewMetrics run")
        library = targets[1]
        labels = ("Unsafe lines", "Unsafe calls", "Unsafe casts", "Pointer arithmetic",
                  "Raw pointer declarations", "Raw pointer dereferences", "Total spans")
        for label in labels:
            if len(re.findall(rf"(?m)^{label}: [0-9]+$", library)) != 1:
                raise SystemExit(f"Missing or ambiguous NewMetrics field: {label}")
        summary = Path(tmp) / "summary.json"
        subprocess.run([sys.executable, str(aggregate), "--out", str(summary)],
                       input=library, text=True, stdout=subprocess.DEVNULL, check=True)
        totals = json.loads(summary.read_text())
    offenders = analyse(Path.cwd()).get("offenders", [])
    for offender in offenders:
        offender["kind"] = "lexical location hint: " + offender["kind"]
    print(json.dumps({"totals": totals, "offenders": offenders}))


if __name__ == "__main__":
    main()
