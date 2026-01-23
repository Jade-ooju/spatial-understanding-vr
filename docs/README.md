# Video Pipeline Documentation

This directory contains essential documentation for the SAM 3 + VLM Video Pipeline project.

## Documentation Index

### Getting Started
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference commands and common usage
- **[VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md)** - Complete usage guide with examples
- **[SETUP_WINDOWS.md](SETUP_WINDOWS.md)** - Windows setup guide with GPU support

### Architecture & Design
- **[VIDEO_POST_PROCESSING_ANALYSIS.md](VIDEO_POST_PROCESSING_ANALYSIS.md)** - Complete pipeline analysis and architecture

### Project Organization
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project structure and organization
- **[SETUP.md](SETUP.md)** - GitHub repository setup guide (optional)

## Quick Start

1. Activate environment:
   ```bash
   conda activate sam3
   ```

2. Run the pipeline:
   ```bash
   python scripts/video_pipeline.py \
     --video resources/VR_short.mkv \
     --prompt "spoon" \
     --output outputs/analysis.mp4
   ```

3. View results:
   ```bash
   vlc outputs/analysis.mp4
   ```

## Pipeline Overview

The video pipeline processes VR headset videos through the following stages:

1. **Initialization**: Loads SAM 3 model and VLM (if available)
2. **Multi-Object Detection**: Detects hands and target objects using separate SAM 3 sessions
3. **Frame Processing**: Processes each frame with masks, VLM analysis, and visualization
4. **Output**: Generates annotated video with AR HUD overlays

## Key Components

### video_pipeline.py
Main pipeline orchestrator that:
- Integrates SAM 3 for object segmentation
- Applies negative masking (black background) for VLM
- Runs VLM analysis for physical properties (every 30 frames by default)
- Creates annotated output video with AR HUD overlays

### multi_object_detector.py
Handles separate SAM 3 sessions for:
- Hand detection (prompt: "hand")
- Target object detection (custom prompt, e.g., "spoon")

### physics_estimator.py
VLM wrapper class that:
- Supports Moondream2 integration (optional)
- Provides placeholder mode when VLM not available
- Analyzes material, weight, and situation properties

## Performance Characteristics

- **SAM 3 Propagation**: Processes entire video in one session (main bottleneck)
- **VLM Analysis**: Runs every 30 frames by default (configurable via `--vlm-interval`)
- **Frame Processing**: Fast visualization and video writing (real-time capable)
- **Memory**: SAM 3 loads entire video into memory (session-based API)

## Historical Documentation

Historical test results, implementation notes, and deprecated documentation have been moved to the `archive/` folder. See `archive/ARCHIVED_DOCS_README.md` for details.
