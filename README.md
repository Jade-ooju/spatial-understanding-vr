# Spatial Understanding for VR

A video processing pipeline for analyzing first-person VR headset videos using SAM 3 (Segment Anything Model 3) and VLM (Vision Language Model) for object segmentation and physical property analysis.

## Features

- **Object Segmentation**: Detect and segment objects in VR videos using SAM 3
- **Physical Property Analysis**: Analyze material and weight using VLM
- **Real-time Visualization**: View results with mask contours and text overlays
- **Performance Tracking**: Complete timing information for all processing steps

## Requirements

- Python 3.8+
- SAM 3 (install via pip)
- OpenCV
- PyTorch
- NumPy
- Moondream2

## Installation

### 1. Install SAM 3

```bash
# Install SAM 3 from official repository
pip install git+https://github.com/facebookresearch/sam3.git

# Or if you have it locally
pip install -e /path/to/sam3
```

### 2. Install Other Dependencies

```bash
pip install opencv-python transformers torch numpy
```

### 3. Authenticate with Hugging Face

```bash
# Required for SAM 3 model downloads
hf auth login
```

## Usage

### Basic Usage

```bash
python scripts/video_pipeline.py \
  --video path/to/video.mp4 \
  --prompt "spoon" \
  --output outputs/result.mp4
```

### Options

- `--video`: Path to video file (required)
- `--prompt`: Text prompt for object detection (default: "spoon")
- `--vlm-interval`: Run VLM every N frames (default: 30)
- `--output`: Output video path (optional)
- `--no-display`: Disable display window
- `--max-frames`: Limit processing to N frames (for testing)

### Example

```bash
# Process VR video for spoon detection
python scripts/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --vlm-interval 30 \
  --output outputs/spoon_analysis.mp4
```

## Project Structure

```
.
├── README.md # This file
├── SAM3_LICENSE # SAM 3 license (required)
├── .gitignore # Git ignore file
│
├── scripts/ # All scripts (pipeline + utilities)
│ ├── video_pipeline.py # Main pipeline orchestrator
│ ├── multi_object_detector.py # Multi-object detection
│ ├── physics_estimator.py # VLM wrapper
│ ├── install_sam3.sh # Installation helper (Linux)
│ ├── install_sam3_windows.ps1 # Installation helper (Windows)
│ ├── verify_setup.ps1 # Setup verification
│ ├── crop_video.py # Video preprocessing
│ └── render_diagrams.py # Diagram rendering utility
│
├── docs/ # Documentation
│ ├── README.md # Documentation index
│ ├── QUICK_REFERENCE.md # Quick reference
│ ├── VIDEO_PIPELINE_USAGE.md # Usage guide
│ ├── VIDEO_POST_PROCESSING_ANALYSIS.md # Complete analysis
│ ├── SETUP.md # GitHub repository setup
│ ├── SETUP_WINDOWS.md # Windows setup guide
│ └── PROJECT_STRUCTURE.md # Project organization
│
├── diagrams/ # Rendered UML diagrams
│ ├── high_level_overview.png # High-level overview
│ ├── pipeline_flow.png # Detailed flow diagram
│ ├── HIGH_QUALITY_DIAGRAMS.md # Diagram guide
│ └── ... # Other diagrams (PNG/SVG)
│
├── tests/ # Test scripts
│ ├── test_my_vr_image.py # VR image test
│ ├── test_ar_hud.py # AR HUD test
│ └── README.md # Test documentation
│
├── archive/ # Historical/deprecated files
│ └── README.md # Archive documentation
│
└── resources/ # Input videos (not in git)
 └── README.md # Resources info
```

## Documentation

See [`docs/`](docs/) for complete documentation:
- [Documentation Index](docs/README.md) - Complete documentation list
- [Quick Reference](docs/QUICK_REFERENCE.md) - Quick start commands
- [Usage Guide](docs/VIDEO_PIPELINE_USAGE.md) - Complete usage instructions
- [Windows Setup](docs/SETUP_WINDOWS.md) - Windows setup guide with GPU support
- [Pipeline Analysis](docs/VIDEO_POST_PROCESSING_ANALYSIS.md) - Complete pipeline analysis
- [Project Structure](docs/PROJECT_STRUCTURE.md) - Project organization

## License

### SAM 3

This project uses [SAM 3 (Segment Anything Model 3)](https://github.com/facebookresearch/sam3) by Meta AI Research.

**SAM 3 License**: See [SAM3_LICENSE](SAM3_LICENSE) for the complete license terms.

**Key Points**:
- SAM 3 is used under the SAM License
- Copyright (c) Meta Platforms, Inc. and affiliates. All Rights Reserved.
- This derivative work complies with SAM 3 license requirements
- See [SAM 3 repository](https://github.com/facebookresearch/sam3) for more information


## Acknowledgments

- [SAM 3](https://github.com/facebookresearch/sam3) by Meta AI Research for object segmentation
- [Moondream2](https://github.com/vikhyat/moondream) for VLM capabilities

