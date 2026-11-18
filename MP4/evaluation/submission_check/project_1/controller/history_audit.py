#!/usr/bin/env python3
"""Count historical model events and iteration attempts without conflating them."""
from collections import Counter
import json
from pathlib import Path
import re

MP4 = Path(__file__).resolve().parent.parent


def main():
    for n in (1, 2):
        rows = []; totals = Counter()
        for path in sorted((MP4 / f"trajectories/project_{n}").glob("run_*/trajectory.jsonl")):
            events = []; malformed = 0
            for line in path.read_text().splitlines():
                if not line.strip(): continue
                try: events.append(json.loads(line))
                except json.JSONDecodeError: malformed += 1
            llm = [e for e in events if e.get("event") == "llm"]
            pipeline_log = path.parent / "pipeline.log"
            attempts = set(re.findall(r"=== iteration (\d+)/", pipeline_log.read_text())) if pipeline_log.exists() else set()
            row = {"run": path.parent.name, "successful_llm_events": len(llm),
                   "iterations_with_llm_event": len({e["iteration"] for e in llm}),
                   "iteration_attempts_in_pipeline_log": len(attempts),
                   "completed_model_turn_events": sum(e.get("event") == "completed_turn" for e in events),
                   "api_attempt_events": sum(e.get("event") == "api_attempt" for e in events),
                   "malformed_log_lines": malformed,
                   "checks": sum(e.get("event") == "checks" for e in events),
                   "stop_events": [e for e in events if e.get("event") == "stop"]}
            rows.append(row)
            totals.update({key: row[key] for key in ("successful_llm_events", "iterations_with_llm_event", "iteration_attempts_in_pipeline_log")})
        out = {"project": n, "totals": dict(totals), "runs": rows,
               "definitions": "Iteration attempts are unique iteration banners per run, not completion. Iterations with llm events had >=1 successful response. Successful llm events include read followups. Legacy runs do not log every HTTP attempt or completed turn, so exact historical API-attempt and completed-turn totals are unknown; zero such event counts means uninstrumented, not zero calls."}
        (MP4 / f"evaluation/history_project_{n}.json").write_text(json.dumps(out, indent=2) + "\n")
        print(n, dict(totals))


if __name__ == "__main__":
    main()
