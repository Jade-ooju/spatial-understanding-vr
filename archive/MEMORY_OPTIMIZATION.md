# GPU Memory Optimization for Windows

## Current Issue

The pipeline is hitting CUDA out of memory errors on RTX 4070 (12GB VRAM) when processing the full video.

**Error**: `CUDA out of memory. Tried to allocate 380.00 MiB. GPU 0 has a total capacity of 11.99 GiB`

## Solutions

### Solution 1: Enable Expandable Segments (Recommended)

This helps with memory fragmentation:

```powershell
# Set environment variable before running
$env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
python video_pipeline/video_pipeline.py --video resources/VR.mkv --prompt "spoon" --output outputs/spoon_analysis.mp4 --vlm-interval 30
```

Or set it permanently in PowerShell:
```powershell
[System.Environment]::SetEnvironmentVariable('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True', 'User')
```

### Solution 2: Process Smaller Video Segments

Instead of processing the entire 1294-frame video at once, process it in chunks:

```powershell
# Process first 30 frames
python video_pipeline/video_pipeline.py --video resources/VR.mkv --prompt "spoon" --output outputs/spoon_part1.mp4 --max-frames 30

# Then process next 30 frames (would need to modify script to start from frame 30)
# Or use video editing tools to split the video first
```

### Solution 3: Clear GPU Cache Before Running

```powershell
# Clear GPU cache
python -c "import torch; torch.cuda.empty_cache(); print('GPU cache cleared')"

# Then run pipeline
python video_pipeline/video_pipeline.py --video resources/VR.mkv --prompt "spoon" --output outputs/spoon_analysis.mp4 --vlm-interval 30
```

### Solution 4: Reduce Batch Size or Resolution

If the video pipeline supports it, you could:
- Process at lower resolution (e.g., 1280x720 instead of 1920x1080)
- Reduce the number of objects tracked simultaneously

### Solution 5: Close Other GPU Applications

Make sure no other applications are using the GPU:
- Close other ML/AI applications
- Close games
- Close video players with GPU acceleration
- Check with: `nvidia-smi`

## Performance Observations

With Triton working:
- **Model initialization**: ~10 seconds (cached)
- **Video loading**: ~36 seconds for 1294 frames
- **Propagation speed**: ~24 seconds per frame (5 frames processed before OOM)
- **GPU memory usage**: ~25GB allocated (exceeds 12GB capacity - memory leak?)

## Memory Analysis

The error shows:
- **Total GPU capacity**: 11.99 GiB
- **PyTorch allocated**: 25.31 GiB (this is suspicious - exceeds GPU capacity!)
- **Reserved but unallocated**: 373.65 MiB

This suggests there might be a memory leak or the model is trying to allocate more than the GPU can hold.

## Recommended Approach

1. **First, try Solution 1** (expandable segments) - this is the easiest
2. **If that doesn't work**, process the video in smaller chunks (Solution 2)
3. **Monitor GPU memory** with `nvidia-smi` during processing
4. **Consider using the shorter test video** (`VR_short.mkv` with 122 frames) first

## Testing with Short Video

```powershell
# If you have VR_short.mkv (122 frames), test with that first
python video_pipeline/video_pipeline.py --video resources/VR_short.mkv --prompt "spoon" --output outputs/spoon_short.mp4 --vlm-interval 30
```

This should work without memory issues and give you a baseline for performance.

## References

- [PyTorch Memory Management](https://pytorch.org/docs/stable/notes/cuda.html#environment-variables)
- [Triton Windows Installation](https://github.com/woct0rdho/triton-windows)






