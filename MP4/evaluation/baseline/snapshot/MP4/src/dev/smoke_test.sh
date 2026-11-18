#!/usr/bin/env bash
# Offline plumbing test: runs the controller against a scripted fake LLM (no API key, no network).
# Writes only to /tmp/smoke, never to MP4/translations or MP4/trajectories.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MP4="$(cd "$HERE/../.." && pwd)"
[[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"
rm -rf /tmp/smoke && mkdir -p /tmp/smoke
python3 "$HERE/mock_llm_server.py" 8765 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1
LLM_BASE_URL=http://127.0.0.1:8765/v1 LLM_MODEL=mock LLM_FALLBACK_MODELS= \
  python3 "$MP4/src/agent.py" --project cset --subject "$MP4/subjects/project_1" \
  --out /tmp/smoke/out --log /tmp/smoke/log --target-dir /tmp/smoke/target --max-iterations 4 --fresh || true
