#!/usr/bin/env python3
"""Offline evaluation of exact submitted snapshots; never makes model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import shlex
import subprocess
import sys
from datetime import datetime, timezone

from regression_results import run_additional_check
from tools import CargoTools, Workspace, cargo_env, run_cmd, sha256_file, unsafe_primary_total

MP4 = Path(__file__).resolve().parent.parent


def evaluate(project_id: int, cfg: dict, output: Path) -> dict:
    project = json.loads((MP4 / "configs/projects.json").read_text())["projects"][str(project_id)]
    crate, subject = MP4 / project["translation"], MP4 / project["subject"]
    ws = Workspace(crate, subject, cfg)
    ws.snapshot_protected()
    cargo = CargoTools(crate, cfg["toolchain"], MP4 / ".runtime/target" / project["name"], cfg)
    output.mkdir(parents=True, exist_ok=False)
    for p in Path(__file__).parent.glob("*.py"):
        controller_copy = output / "controller" / p.name
        controller_copy.parent.mkdir(parents=True, exist_ok=True)
        controller_copy.write_bytes(p.read_bytes())
    hashes = {p.relative_to(crate).as_posix(): sha256_file(p) for p in crate.rglob("*")
              if p.is_file() and "target" not in p.relative_to(crate).parts}
    for p in crate.rglob("*"):
        if p.is_file() and "target" not in p.relative_to(crate).parts:
            q = output / "snapshot" / p.relative_to(crate)
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(p.read_bytes())
    result = {
        "project": project["name"], "project_id": project_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=MP4, text=True).strip(),
        "python": sys.version, "platform": platform.platform(), "config": cfg,
        "implementation_sha256": hashes,
        "controller_sha256": {p.name: sha256_file(p) for p in Path(__file__).parent.glob("*.py")},
        "subject_sha256": {p.relative_to(subject).as_posix(): sha256_file(p) for p in subject.rglob("*") if p.is_file()},
        "policy": ws.protected_violations() + ws.forbidden_findings(),
        "interface": ws.interface_findings(), "stubs": ws.stub_findings(),
    }
    def save():
        (output / "evaluation.json").write_text(json.dumps(result, indent=2) + "\n")
    save()
    for name, method in (("build", cargo.build), ("test", cargo.test), ("clippy", cargo.clippy), ("unsafe", cargo.unsafe_metrics)):
        print(f"{project['name']}: {name}", flush=True)
        result[name] = method()
        save()
    result["additional_checks"] = []
    for i, command in enumerate(cfg.get("additional_checks", [])):
        result["additional_checks"].append(run_additional_check(
            command, output=(output / "additional_checks" / str(i)).resolve(), project_id=project_id,
            crate=crate, mp4=MP4, python=sys.executable, env=cargo.env, timeout=cfg["limits"]["command_timeout_s"],
        ))
        save()
    versions = {}
    for name, cmd in {
        "rustc": ["rustc", f"+{cfg['toolchain']}", "-Vv"],
        "cargo": ["cargo", f"+{cfg['toolchain']}", "--version"],
        "clippy": ["cargo", f"+{cfg['toolchain']}", "clippy", "--version"],
        "rustfmt": ["cargo", f"+{cfg['toolchain']}", "fmt", "--version"],
    }.items():
        versions[name] = run_cmd(cmd, crate, cargo.env, 30)
    result["versions"] = versions
    result["unsafe_primary_total"] = unsafe_primary_total(result["unsafe"])
    result["source_hashes_unchanged"] = all((crate / p).is_file() and sha256_file(crate / p) == h for p, h in hashes.items())
    result["mandatory_validation_clean"] = (
        all(result[k].get("ok") for k in ("build", "test", "clippy"))
        and result["unsafe"].get("valid") and result["unsafe"].get("tool") == "official"
        and result["unsafe_primary_total"] == 0 and result["clippy"]["total"] <= cfg["stopping_condition"]["clippy_accept"]
        and not any(result[k] for k in ("policy", "interface", "stubs")) and result["source_hashes_unchanged"]
        and all(c["ok"] for c in result["additional_checks"])
    )
    save()
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path, help="new evidence directory; never overwrites results")
    ap.add_argument("--config", type=Path, default=MP4 / "configs/pipeline.json")
    ap.add_argument("--project-id", type=int, choices=[1, 2])
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cfg = json.loads(args.config.read_text())
    results = [evaluate(n, cfg, args.output / f"project_{n}") for n in ([args.project_id] if args.project_id else [1, 2])]
    validator = cfg.get("submission_validator", {}).get("command")
    validation = run_cmd(shlex.split(validator.replace("{path}", str(MP4))), MP4, cargo_env(MP4 / ".runtime/target/validator"), 300) if validator else {"available": False, "error": "instructor validator not configured"}
    summary = {"projects": [{"project": r["project"], "build_ok": r["build"]["ok"],
                             "test_returncode": r["test"]["returncode"], "passed": r["test"]["passed"], "total": r["test"]["total"],
                             "distinct_passed": r["test"]["distinct_passed"], "distinct_total": r["test"]["distinct_total"],
                             "clippy": r["clippy"]["counts"], "clippy_ok": r["clippy"]["ok"],
                             "safety_tool": r["unsafe"].get("tool"), "mandatory_validation_clean": r["mandatory_validation_clean"]} for r in results],
               "instructor_validator": validation}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0 if all(r["mandatory_validation_clean"] for r in results) and validation.get("returncode") == 0 and not validation.get("timed_out", True) else 1


if __name__ == "__main__":
    sys.exit(main())
