# Spatial Understanding for VR

A video processing pipeline for analyzing first-person VR headset videos using SAM 3 (Segment Anything Model 3) and VLM (Vision Language Model) for object segmentation and physical property analysis.

## 🎯 Features

- **Object Segmentation**: Detect and segment objects in VR videos using SAM 3
- **Physical Property Analysis**: Analyze material and weight using VLM
- **Real-time Visualization**: View results with mask contours and text overlays
- **Performance Tracking**: Complete timing information for all processing steps

## 📋 Requirements

- Python 3.8+
- SAM 3 (install via pip)
- OpenCV
- PyTorch
- NumPy
- Moondream2 (optional, for VLM)

## 🚀 Installation

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

## 💻 Usage

### Basic Usage

```bash
python scripts/video_pipeline/video_pipeline.py \
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
python scripts/video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --vlm-interval 30 \
  --output outputs/spoon_analysis.mp4
```

## 📁 Project Structure

```
.
├── scripts/video_pipeline/      # Pipeline scripts
│   ├── video_pipeline.py        # Main pipeline
│   ├── physics_estimator.py     # VLM wrapper
│   └── monitor_progress.sh      # Progress monitor
├── docs/video_pipeline/         # Documentation
├── outputs/video_pipeline/      # Output files
└── resources/                   # Input videos (not in repo)
```

## 📚 Documentation

See [`docs/video_pipeline/`](docs/video_pipeline/) for complete documentation:
- [Quick Reference](docs/video_pipeline/QUICK_REFERENCE.md)
- [Usage Guide](docs/video_pipeline/VIDEO_PIPELINE_USAGE.md)
- [Results](docs/video_pipeline/FINAL_RESULTS.md)

## ⚖️ License & Attribution

### This Project

[YOUR LICENSE HERE - e.g., MIT License]

### SAM 3

This project uses [SAM 3 (Segment Anything Model 3)](https://github.com/facebookresearch/sam3) by Meta AI Research.

**SAM 3 License**: See [SAM3_LICENSE](SAM3_LICENSE) for the complete license terms.

**Key Points**:
- SAM 3 is used under the SAM License
- Copyright (c) Meta Platforms, Inc. and affiliates. All Rights Reserved.
- This derivative work complies with SAM 3 license requirements
- See [SAM 3 repository](https://github.com/facebookresearch/sam3) for more information

### Attribution

If you use this code in research, please cite:

```bibtex
@article{sam3,
  title={SAM 3: Segment Anything with Concepts},
  author={Meta AI Research},
  year={2025},
  url={https://ai.meta.com/sam3}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 Citation

If you use this project in your research, please cite:

```bibtex
@software{spatial_understanding_vr,
  title={Spatial Understanding for VR: Video Pipeline with SAM 3 and VLM},
  author={Your Name},
  year={2025},
  url={https://github.com/Jade-ooju/spatial-understanding-vr}
}
```

## 🙏 Acknowledgments

- [SAM 3](https://github.com/facebookresearch/sam3) by Meta AI Research for object segmentation
- [Moondream2](https://github.com/vikhyat/moondream) for VLM capabilities (optional)

## 📧 Contact

[Your contact information]

## ⚠️ Disclaimer

This project is provided "as is" without warranty of any kind. See LICENSE files for details.

