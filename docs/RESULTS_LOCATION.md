# Where to Find Video Pipeline Results

## Results Location

### 1. **Output Video File** (Main Result)
**Location**: `outputs/spoon_analysis.mp4`

This file contains:
- Original video frames
- **Green mask contours** around detected "spoon" objects
- **VLM text overlay** showing:
  - Material: [analyzed material]
  - Weight: [analyzed weight]

**How to view**: Open with any video player (VLC, mpv, etc.)

### 2. **Console Output / Log File**
**Location**: `outputs/test_results_with_timing.log`

Contains:
- Timing information for each step
- VLM analysis results for each frame
- Progress updates
- Error messages (if any)

**Key timing information includes**:
- SAM 3 model initialization time
- Video session loading time
- Propagation time (per frame and total)
- VLM analysis time (per call)
- Total processing time

### 3. **Real-time Display** (if `--no-display` not used)
Shows the annotated video in a window with:
- Green contours around detected objects
- VLM text overlay
- Press 'q' to quit, 'p' to pause

## Expected Timing (for 122 frames @ 1920x1080)

Based on initial tests:
- **Model initialization**: ~5-7 seconds
- **Session loading**: ~2-3 seconds (loading 122 frames)
- **Propagation**: ~30 seconds per frame = **~1 hour for 122 frames**
- **VLM analysis**: ~0.1-0.5 seconds per call (every 30 frames)
- **Frame processing/visualization**: <0.1 seconds per frame

**Total estimated time**: ~1-1.5 hours for 122 frames

## Checking Progress

```bash
# Check log file for progress
tail -f test_results_with_timing.log

# Check if output video is being created
ls -lh outputs/spoon_analysis.mp4

# Check process status
ps aux | grep video_pipeline
```

## Results Format

### VLM Results (printed to console/log)
```
Frame 0: VLM result - {'material': 'metallic or shiny medium object', 'weight': 'light to medium'} (0.15s)
Frame 30: VLM result - {'material': 'metallic or shiny medium object', 'weight': 'light to medium'} (0.12s)
```

### Timing Summary (at end of processing)
```
✓ Propagation complete: 122 frames processed (3660.00 seconds, 0.03 frames/sec)
✓ Processed 122 frames (12.20 seconds, 10.00 frames/sec)
VLM analysis: 5 calls, avg 0.13s per call, total 0.65s
```

## After Completion

Once the process completes, you will have:
1. ✅ `outputs/spoon_analysis.mp4` - Annotated video with results
2. ✅ `test_results_with_timing.log` - Complete log with all timing information

## Viewing Results

```bash
# View the output video
vlc outputs/spoon_analysis.mp4
# or
mpv outputs/spoon_analysis.mp4

# View timing summary
grep -E "seconds|frames/sec|VLM result" outputs/test_results_with_timing.log | tail -20
```

