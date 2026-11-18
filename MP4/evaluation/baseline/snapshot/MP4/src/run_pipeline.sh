#!/usr/bin/env bash
# Reproduce the agentic C -> Rust pipeline for one assigned project.
#
#   bash MP4/src/run_pipeline.sh 1            # project_1 (cset)
#   bash MP4/src/run_pipeline.sh 2            # project_2 (libpsbt)
#   bash MP4/src/run_pipeline.sh 1 --fresh    # discard the existing translation first
#
# Needs: python3 (3.9+), rustup with toolchain nightly-2025-05-13 (+clippy), and an API key in
# $OPENROUTER_API_KEY (or whichever variable configs/pipeline.json names). Never commit the key.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <project-id: 1|2> [extra agent.py flags, e.g. --fresh --max-iterations 10]" >&2
  exit 2
fi
PROJECT_ID="$1"; shift

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$HOME/.cargo/env" ]]; then source "$HOME/.cargo/env"; fi

TOOLCHAIN="$(python3 -c "import json,sys; print(json.load(open('$HERE/../configs/pipeline.json'))['toolchain'])")"
if ! rustup toolchain list | grep -q "$TOOLCHAIN"; then
  echo "installing Rust toolchain $TOOLCHAIN ..."
  rustup toolchain install "$TOOLCHAIN" --profile minimal -c clippy -c rustfmt
fi

exec python3 "$HERE/agent.py" --project-id "$PROJECT_ID" "$@"
