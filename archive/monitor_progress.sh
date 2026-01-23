#!/bin/bash
# Monitor video pipeline progress
# Usage: Run from repository root: ./video_pipeline/monitor_progress.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Log and output files (adjust paths as needed for your setup)
LOG_FILE="${LOG_FILE:-$REPO_ROOT/outputs/test_results_with_timing.log}"
OUTPUT_FILE="${OUTPUT_FILE:-$REPO_ROOT/outputs/spoon_analysis.mp4}"

echo "=== Video Pipeline Progress Monitor ==="
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo "Log file not found. Process may not have started yet."
    exit 1
fi

echo "--- Latest Progress ---"
tail -10 "$LOG_FILE" | grep -E "Processed|Propagation|VLM result|seconds|Complete" || tail -5 "$LOG_FILE"

echo ""
echo "--- Timing Summary (so far) ---"
grep -E "initialized|Session started|Propagation complete|Processed.*frames|VLM analysis" "$LOG_FILE" | tail -10

echo ""
echo "--- Output File Status ---"
if [ -f "$OUTPUT_FILE" ]; then
    ls -lh "$OUTPUT_FILE"
    echo "✓ Output video file exists"
else
    echo "⏳ Output video not created yet (will be created during frame processing)"
fi

echo ""
echo "--- Process Status ---"
if pgrep -f "video_pipeline.py" > /dev/null; then
    echo "✓ Process is running"
    ps aux | grep video_pipeline.py | grep -v grep | awk '{print "  PID:", $2, "CPU:", $3"%", "MEM:", $4"%"}'
else
    echo "✗ Process not running (may have completed or crashed)"
fi

