#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if command -v uv >/dev/null 2>&1; then
  exec uv run python scripts/run_pipeline.py -c g1_pullover_dance_real
elif [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python scripts/run_pipeline.py -c g1_pullover_dance_real
else
  exec python3 scripts/run_pipeline.py -c g1_pullover_dance_real
fi
