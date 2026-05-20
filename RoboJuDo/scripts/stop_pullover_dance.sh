#!/usr/bin/env bash
set -euo pipefail
pattern=scripts/run_pipeline.py -c g1_pullover_dance_real
pids=$(pgrep -f "$pattern" || true)
if [[ -z "$pids" ]]; then
  echo "No pullover dance pipeline process found."
  exit 0
fi
echo "Stopping pullover dance pipeline: $pids"
kill -INT $pids || true
sleep 2
remaining=$(pgrep -f "$pattern" || true)
if [[ -n "$remaining" ]]; then
  echo "Force-stopping remaining process: $remaining"
  kill -TERM $remaining || true
fi
