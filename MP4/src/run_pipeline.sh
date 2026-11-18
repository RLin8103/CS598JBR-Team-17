#!/usr/bin/env bash
# Reproduce the agentic C -> Rust pipeline for one assigned project.
#
#   bash MP4/src/run_pipeline.sh 1            # project_1 (cset)
#   bash MP4/src/run_pipeline.sh 2            # project_2 (libpsbt)
#   bash MP4/src/run_pipeline.sh 1 --fresh    # discard the existing translation first
#
# Needs: Python 3.10+, rustup with toolchain nightly-2025-05-13 (+clippy/rustfmt), and an API key in
# $OPENROUTER_API_KEY (or whichever variable configs/pipeline.json names). Never commit the key.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <project-id: 1|2> [extra agent.py flags, e.g. --fresh --max-iterations 10]" >&2
  exit 2
fi
PROJECT_ID="$1"; shift

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MP4_ROOT="$(cd "$HERE/.." && pwd)"
PYTHON_BIN="${CRUST_PYTHON:-$MP4_ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then PYTHON_BIN="python3"; fi
if [[ -x "$MP4_ROOT/.runtime/cargo/bin/rustup" ]]; then
  export CARGO_HOME="$MP4_ROOT/.runtime/cargo"
  export RUSTUP_HOME="$MP4_ROOT/.runtime/rustup"
  export PATH="$CARGO_HOME/bin:$PATH"
elif [[ -f "$HOME/.cargo/env" ]]; then
  source "$HOME/.cargo/env"
fi

TOOLCHAIN="nightly-2025-05-13"
if ! command -v rustup >/dev/null || ! rustup run "$TOOLCHAIN" rustc --version >/dev/null; then
  echo "Missing $TOOLCHAIN. See MP4/README.md for the local installation command." >&2
  exit 2
fi

exec "$PYTHON_BIN" "$HERE/agent.py" --project-id "$PROJECT_ID" "$@"
