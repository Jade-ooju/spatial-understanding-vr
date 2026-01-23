# Testing the Video Pipeline

This guide shows you how to test the SAM 3 + VLM video pipeline with your VR recorded videos.

## Quick Start

### 1. Prepare Your Video

Place your VR video file in a location accessible to the script. For example:
- Create a `resources` folder: `spatial-understanding-vr/resources/`
- Or use the full path to your video file

Supported formats: MP4, MKV, AVI, MOV, etc.

### 2. Activate Environment

```powershell
conda activate sam3
cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr
```

### 3. Run the Pipeline

**Basic usage:**
```powershell
python video_pipeline/video_pipeline.py --video "path/to/your/video.mp4" --prompt "spoon"
```

**With output video:**
```powershell
python video_pipeline/video_pipeline.py `
 --video "path/to/your/video.mp4" `
 --prompt "spoon" `
 --output outputs/result.mp4
```

**Test with limited frames (faster):**
```powershell
python video_pipeline/video_pipeline.py `
 --video "path/to/your/video.mp4" `
 --prompt "spoon" `
 --max-frames 50 `
 --output outputs/test_result.mp4
```

**Without display (headless):**
```powershell
python video_pipeline/video_pipeline.py `
 --video "path/to/your/video.mp4" `
 --prompt "spoon" `
 --no-display `
 --output outputs/result.mp4
```

## Command-Line Arguments

- `--video` (required): Path to your video file
- `--prompt` (optional): Text prompt for SAM 3 (default: "spoon")
 - Examples: "spoon", "cup", "hand", "bottle", "phone"
- `--vlm-interval` (optional): Run VLM every N frames (default: 30)
 - Lower = more frequent analysis but slower
 - Higher = faster but less frequent analysis
- `--output` (optional): Path to save annotated video
 - If not specified, video is only displayed (not saved)
- `--max-frames` (optional): Limit processing to first N frames
 - Useful for quick testing
- `--no-display`: Disable real-time display window

## Example Commands

### Example 1: Detect a spoon in your video
```powershell
python video_pipeline/video_pipeline.py `
 --video "D:\Videos\my_vr_recording.mp4" `
 --prompt "spoon" `
 --output outputs/spoon_detection.mp4
```

### Example 2: Detect a cup with frequent VLM analysis
```powershell
python video_pipeline/video_pipeline.py `
 --video "D:\Videos\my_vr_recording.mp4" `
 --prompt "cup" `
 --vlm-interval 15 `
 --output outputs/cup_analysis.mp4
```

### Example 3: Quick test (first 30 frames only)
```powershell
python video_pipeline/video_pipeline.py `
 --video "D:\Videos\my_vr_recording.mp4" `
 --prompt "hand" `
 --max-frames 30 `
 --output outputs/test_hand.mp4
```

## What the Pipeline Does

1. **Loads your video** using OpenCV
2. **Initializes SAM 3** video predictor
3. **Initializes VLM** (PhysicsEstimator) for material/weight analysis
4. **Processes each frame:**
 - Detects objects using SAM 3 with your text prompt
 - Extracts masks (object boundaries)
 - Applies negative masking (black background)
 - Runs VLM analysis every N frames to estimate material/weight
 - Visualizes results with green contours and text overlays
5. **Saves output video** (if `--output` specified)

## Output

The pipeline will:
- Display real-time visualization (unless `--no-display` is used)
- Show green contours around detected objects
- Display material/weight analysis text overlay
- Save annotated video to specified output path
- Print timing information to console

## Troubleshooting

### Video not found
```
Error: Video not found: path/to/video.mp4
```
**Solution:** Check the video path. Use absolute path or relative path from project directory.

### SAM 3 not found
```
Error: SAM 3 not found. Make sure you're in the sam3 conda environment.
```
**Solution:** 
```powershell
conda activate sam3
```

### CUDA out of memory
```
RuntimeError: CUDA out of memory
```
**Solution:** 
- Use `--max-frames` to process fewer frames
- Close other GPU applications
- Process shorter video segments

### VLM not working
```
Warning: VLM not initialized
```
**Solution:**
- Check Hugging Face authentication: `hf auth login`
- Verify transformers installed: `pip install transformers pillow`

## Performance Tips

- **First run is slow**: SAM 3 model loads on first use (~30-60 seconds)
- **GPU recommended**: CPU is 100x slower
- **Use `--max-frames`**: Test with 30-50 frames first
- **Adjust `--vlm-interval`**: Higher values = faster processing
- **Use `--no-display`**: Slightly faster without visualization

## Expected Performance

- **With GPU (RTX 4070)**: 5-10 fps processing speed
- **121 frames**: ~2-4 minutes
- **Memory usage**: 6-8GB GPU VRAM

## Next Steps

After successful test:
1. Process full videos with your desired objects
2. Experiment with different prompts
3. Adjust VLM interval based on your needs
4. Review output videos in `outputs/` folder






