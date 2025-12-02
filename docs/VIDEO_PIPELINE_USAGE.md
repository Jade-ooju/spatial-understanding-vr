# Video Pipeline Usage Guide

## Overview

The `video_pipeline.py` script processes VR headset videos to:
1. Segment objects using SAM 3 (e.g., "spoon")
2. Extract objects with black backgrounds
3. Analyze physical properties using VLM (Moondream2)

## Prerequisites

1. **Activate the sam3 conda environment:**
   ```bash
   conda activate sam3
   ```

2. **Ensure dependencies are installed:**
   - SAM 3 (already installed in the environment)
   - OpenCV: `pip install opencv-python`
   - Moondream2 (optional, for VLM): `pip install transformers torch`

## Basic Usage

### Process video with default settings:
```bash
# From repository root
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon"
```

### Process video with custom VLM interval:
```bash
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --vlm-interval 30
```

### Save output video:
```bash
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --output outputs/annotated_video.mp4
```

### Run without display (headless):
```bash
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --no-display \
  --output outputs/annotated_video.mp4
```

## Command-Line Arguments

- `--video`: Path to video file (MP4, MKV, etc.) or JPEG folder (required)
- `--prompt`: Text prompt for SAM 3 (default: "spoon")
- `--vlm-interval`: Run VLM every N frames (default: 30)
- `--no-display`: Disable real-time display
- `--output`: Optional path to save annotated video

## Workflow

1. **Video Loading**: Opens video file with OpenCV
2. **SAM 3 Session**: Starts session and loads entire video
3. **Text Prompt**: Adds text prompt (e.g., "spoon") on frame 0
4. **Propagation**: Propagates tracking through entire video
5. **Frame Processing**:
   - Extracts mask for each frame
   - Applies negative masking (black background)
   - Runs VLM every N frames (default: 30)
   - Visualizes with green contours and VLM text overlay
6. **Display**: Shows real-time visualization (press 'q' to quit, 'p' to pause)

## Controls

- **'q'**: Quit
- **'p'**: Pause/Resume

## Output

The script displays:
- Green mask contours around detected objects
- VLM analysis text overlay showing:
  - Material: [material type]
  - Weight: [weight estimate]

## Example: Processing VR Video for Spoon Detection

```bash
# Basic usage
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon"

# With output video
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --output outputs/spoon_analysis.mp4

# Faster processing (VLM every 60 frames instead of 30)
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --vlm-interval 60
```

## Troubleshooting

### "SAM 3 not found"
- Make sure you're in the sam3 conda environment: `conda activate sam3`

### "Video not found"
- Check the video path is correct
- Ensure the video file exists and is readable

### "Could not open video file"
- Check video format is supported (MP4, MKV, AVI, etc.)
- Try converting with ffmpeg: `ffmpeg -i input.mkv output.mp4`

### VLM not working
- The script includes a placeholder PhysicsEstimator
- For actual VLM analysis, install Moondream2: `pip install transformers torch`
- Or implement your own PhysicsEstimator class

### Performance Issues
- Increase `--vlm-interval` to run VLM less frequently
- Use `--no-display` for faster processing
- Ensure GPU is available for SAM 3 (automatically detected)

## Notes

- SAM 3 loads the entire video into memory (session-based API)
- For very long videos, consider splitting into chunks
- VLM analysis is optimized to run every 30 frames by default
- The script handles edge cases: no mask found, multiple objects, etc.

