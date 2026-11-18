"""Validate named outcomes from the separate MP4 evaluation harness."""
import json
from pathlib import Path
import re
import shlex

from tools import process_ok, run_cmd, sha256_file


def source_hashes(crate):
    return {p.relative_to(crate).as_posix(): sha256_file(p)
            for p in sorted((crate / "src").rglob("*.rs")) if p.is_file()}


def named_outcomes(inventory, execution):
    """Require the complete libtest inventory, one result per case and matching totals."""
    if not process_ok(inventory) or execution["timed_out"] or execution.get("interrupted"):
        raise ValueError("harness did not finish")
    names = re.findall(r"^(\S+): test$", inventory["stdout"], re.M)
    records = re.findall(r"^test (\S+) \.\.\. (ok|FAILED)$", execution["stdout"], re.M)
    outcomes = dict(records)
    if not names or len(names) != len(set(names)) or len(records) != len(outcomes) or set(names) != outcomes.keys():
        raise ValueError("missing or duplicate harness results")
    totals = re.findall(r"^test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; 0 ignored; 0 measured;", execution["stdout"], re.M)
    failed = sum(value == "FAILED" for value in outcomes.values())
    expected = ("FAILED" if failed else "ok", str(len(names) - failed), str(failed))
    if totals != [expected] or execution["returncode"] != (101 if failed else 0):
        raise ValueError("harness summary or process status disagrees with case results")
    return outcomes


def run_additional_check(command, *, output, project_id, crate, mp4, python, env, timeout):
    args = [arg.replace("{python}", python).replace("{output}", str(output)).replace("{mp4}", str(mp4))
            .replace("{project_id}", str(project_id)) for arg in shlex.split(command)]
    if not any(Path(arg).resolve() == mp4 / "src/run_regressions.py" for arg in args):
        result = run_cmd(args, mp4, env, timeout)
        return {**result, "ok": process_ok(result)}

    before = source_hashes(crate)
    if output.exists():
        return {"cmd": shlex.join(args), "returncode": None, "timed_out": False, "stdout": "",
                "stderr": "Harness evidence directory already exists", "ok": False, "outcomes": None}
    result = run_cmd(args, mp4, env, timeout)
    result.update(ok=False, outcomes=None)
    try:
        if result["timed_out"] or result.get("interrupted"):
            raise ValueError("regression command was interrupted or timed out")
        evidence = json.loads((output / "results.json").read_text())
        if evidence["source_sha256"][str(project_id)] != before or source_hashes(crate) != before:
            raise ValueError("harness evidence belongs to a different source snapshot")
        if evidence["project_id"] != project_id:
            raise ValueError("harness evidence belongs to a different project")
        if not all(process_ok(evidence[key]) for key in ("c_compile", "c_oracle")):
            raise ValueError("C oracle did not complete")
        outcomes = named_outcomes(evidence["inventory"], evidence["rust"])
        clean = all(value == "ok" for value in outcomes.values())
        if result["returncode"] != (0 if clean else 1):
            raise ValueError("regression driver status disagrees with case results")
        result.update(ok=clean, outcomes=outcomes, source_sha256=before)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        result["validation_error"] = str(error)
    return result
