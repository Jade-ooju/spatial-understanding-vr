# Video Pipeline Documentation

This directory contains all documentation for the SAM 3 + VLM Video Pipeline project.

## 📚 Documentation Index

### Getting Started
- **[VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md)** - Quick start guide and usage instructions
- **[VIDEO_PIPELINE_PLAN.md](VIDEO_PIPELINE_PLAN.md)** - Implementation plan and architecture design

### Results & Testing
- **[FINAL_RESULTS.md](FINAL_RESULTS.md)** - Complete results from test run with timing breakdown
- **[TIMING_RESULTS.md](TIMING_RESULTS.md)** - Detailed timing analysis
- **[RESULTS_LOCATION.md](RESULTS_LOCATION.md)** - Where to find output files and results
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Initial test results and troubleshooting

## 🚀 Quick Start

1. **Activate environment**:
   ```bash
   conda activate sam3
   ```

2. **Run the pipeline**:
   ```bash
   python video_pipeline/video_pipeline.py \
     --video resources/VR_short.mkv \
     --prompt "spoon" \
     --output outputs/analysis.mp4
   ```

3. **View results**:
   ```bash
   vlc outputs/analysis.mp4
   ```

## 📁 Project Structure

```
spatial-understanding-vr/
├── video_pipeline/          # Pipeline scripts
│   ├── video_pipeline.py            # Main pipeline script
│   ├── physics_estimator.py         # VLM wrapper
│   └── monitor_progress.sh          # Progress monitoring
├── outputs/          # Results and logs
│   ├── spoon_analysis.mp4          # Output videos
│   └── test_results_with_timing.log # Log files
└── docs/             # Documentation (this directory)
```

## 🔧 Components

### video_pipeline.py
Main pipeline script that:
- Integrates SAM 3 for object segmentation
- Applies negative masking (black background)
- Runs VLM analysis for physical properties
- Creates annotated output video

### physics_estimator.py
VLM wrapper class that:
- Supports Moondream2 integration
- Provides placeholder mode when VLM not available
- Analyzes material and weight properties

### monitor_progress.sh
Utility script to monitor pipeline progress in real-time.

## 📊 Results

See [FINAL_RESULTS.md](FINAL_RESULTS.md) for complete results from the test run.

**Key Metrics** (for 122 frames @ 1920x1080):
- Total time: ~85.5 minutes
- Propagation: 85.3 minutes (bottleneck)
- Frame processing: 3.84 seconds
- VLM analysis: 0.12 seconds (5 calls)

## 📖 More Information

- **Usage Guide**: [VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md)
- **Architecture**: [VIDEO_PIPELINE_PLAN.md](VIDEO_PIPELINE_PLAN.md)
- **Results**: [FINAL_RESULTS.md](FINAL_RESULTS.md)

