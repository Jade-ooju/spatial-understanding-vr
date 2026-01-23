# Video Pipeline Quick Reference

## Quick Start

```bash
# 1. Activate environment
conda activate sam3

# 2. Run pipeline
python scripts/video_pipeline.py \
  --video resources/VR_short.mkv \
  --prompt "spoon" \
  --output outputs/result.mp4

# 3. View results
vlc outputs/result.mp4
```

## Project Structure

```
spatial-understanding-vr/
├── scripts/ # All scripts
│ ├── video_pipeline.py # Main pipeline script
│ ├── multi_object_detector.py # Multi-object detection
│ ├── physics_estimator.py # VLM wrapper
│ └── ... # Other utility scripts
├── outputs/ # Results (user creates)
│ ├── *.mp4 # Output videos
│ └── *.log # Log files
└── docs/ # Documentation
 ├── README.md # Overview
 └── VIDEO_PIPELINE_USAGE.md # Usage guide
```

## Common Commands

### Basic Usage
```bash
python scripts/video_pipeline.py \
  --video <video_path> \
  --prompt "<object_name>"
```

### With Output
```bash
python scripts/video_pipeline.py \
  --video <video_path> \
  --prompt "<object_name>" \
  --output outputs/result.mp4
```

### Headless Mode
```bash
python scripts/video_pipeline.py \
  --video <video_path> \
  --prompt "<object_name>" \
  --no-display \
  --output outputs/result.mp4
```

### Limit Frames (for testing)
```bash
python scripts/video_pipeline.py \
  --video <video_path> \
  --prompt "<object_name>" \
  --max-frames 100
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--video` | Video file path (required) | - |
| `--prompt` | Text prompt for SAM 3 | "spoon" |
| `--vlm-interval` | Run VLM every N frames | 30 |
| `--output` | Output video path | None |
| `--no-display` | Disable display window | False |
| `--max-frames` | Limit to N frames | None |

## Expected Performance

**For 122 frames @ 1920x1080:**
- Model init: ~7 seconds
- Session start: ~0.5 seconds
- Propagation: ~85 minutes (CPU)
- Frame processing: ~4 seconds
- VLM analysis: ~0.1 seconds

**Total**: ~85-90 minutes

## Output Locations

- **Videos**: `outputs/*.mp4` (user creates this directory)
- **Logs**: `outputs/*.log` (user creates this directory)
- **Documentation**: `docs/`

## Troubleshooting

### "Module not found"
```bash
conda activate sam3
pip install opencv-python
```

### "Video not found"
Check path is correct and file exists.

### Memory issues
Use `--max-frames` to limit processing, or create shorter test video.

### Slow processing
Propagation is slow on CPU (~30-40s per frame). GPU would be much faster.

## More Information

- **Full Usage Guide**: [VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md)
- **Architecture**: [VIDEO_POST_PROCESSING_ANALYSIS.md](VIDEO_POST_PROCESSING_ANALYSIS.md)
- **Project Structure**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

