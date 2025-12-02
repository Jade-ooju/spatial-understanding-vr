# Video Pipeline Organization

This document describes the organization structure of the video pipeline project.

## 📁 Directory Structure

```
spatial-understanding-vr/
├── video_pipeline/          # All pipeline scripts
│   ├── video_pipeline.py            # Main pipeline script
│   ├── physics_estimator.py          # VLM wrapper class
│   ├── monitor_progress.sh          # Progress monitoring utility
│   └── README.md                    # Scripts documentation
│
├── outputs/          # All results and logs
│   ├── spoon_analysis.mp4           # Output video files
│   ├── test_results_with_timing.log # Complete timing logs
│   ├── test_output.log              # Test logs
│   ├── test_short.log               # Short test logs
│   └── README.md                    # Results documentation
│
└── docs/             # All documentation
    ├── README.md                    # Overview and index
    ├── INDEX.md                     # Documentation index
    ├── QUICK_REFERENCE.md           # Quick start commands
    ├── VIDEO_PIPELINE_USAGE.md      # Complete usage guide
    ├── VIDEO_PIPELINE_PLAN.md       # Architecture and design
    ├── FINAL_RESULTS.md             # Test results summary
    ├── TIMING_RESULTS.md            # Performance analysis
    ├── RESULTS_LOCATION.md          # Output file locations
    ├── TEST_RESULTS.md              # Initial test results
    └── ORGANIZATION.md              # This file
```

## 🎯 Organization Principles

### Scripts (`video_pipeline/`)
- **Purpose**: All executable code and utilities
- **Contents**: Python scripts, shell scripts, and their documentation
- **Usage**: Run from project root with full paths

### Results (`outputs/`)
- **Purpose**: All output files from pipeline runs
- **Contents**: Video files, log files, timing data
- **Note**: Separate from other outputs (images, etc.)

### Documentation (`docs/`)
- **Purpose**: Complete documentation for the pipeline
- **Contents**: Usage guides, architecture docs, results analysis
- **Structure**: Organized by topic and use case

## 📝 File Descriptions

### Scripts

| File | Description |
|------|-------------|
| `video_pipeline.py` | Main pipeline script - processes videos with SAM 3 and VLM |
| `physics_estimator.py` | VLM wrapper class for physical property analysis |
| `monitor_progress.sh` | Utility to monitor pipeline progress in real-time |
| `README.md` | Documentation for scripts directory |

### Results

| File | Description |
|------|-------------|
| `spoon_analysis.mp4` | Annotated output video with masks and VLM text |
| `test_results_with_timing.log` | Complete log with all timing information |
| `test_output.log` | Initial test run log |
| `test_short.log` | Short test run log |
| `README.md` | Documentation for results directory |

### Documentation

| File | Description |
|------|-------------|
| `README.md` | Overview and documentation index |
| `INDEX.md` | Complete documentation index with reading order |
| `QUICK_REFERENCE.md` | Quick start commands and common usage |
| `VIDEO_PIPELINE_USAGE.md` | Complete usage guide with examples |
| `VIDEO_PIPELINE_PLAN.md` | Architecture design and implementation plan |
| `FINAL_RESULTS.md` | Complete test results with timing breakdown |
| `TIMING_RESULTS.md` | Detailed performance analysis |
| `RESULTS_LOCATION.md` | Where to find output files |
| `TEST_RESULTS.md` | Initial test results and troubleshooting |
| `ORGANIZATION.md` | This file - organization structure |

## 🔄 Migration Notes

Files were organized from the root directory:

**Moved to `video_pipeline/`:**
- `video_pipeline.py`
- `physics_estimator.py`
- `monitor_progress.sh`

**Moved to `outputs/`:**
- `spoon_analysis.mp4`
- `test_results_with_timing.log`
- `test_output.log`
- `test_short.log`

**Moved to `docs/`:**
- `FINAL_RESULTS.md`
- `TIMING_RESULTS.md`
- `RESULTS_LOCATION.md`
- `TEST_RESULTS.md`
- `VIDEO_PIPELINE_PLAN.md`
- `VIDEO_PIPELINE_USAGE.md`

## ✅ Benefits of This Organization

1. **Clear Separation**: Scripts, results, and docs are clearly separated
2. **Easy Navigation**: Related files are grouped together
3. **Scalability**: Easy to add new scripts, results, or documentation
4. **Maintainability**: Clear structure makes maintenance easier
5. **Documentation**: Each directory has its own README

## 🚀 Usage After Organization

All commands now use the new paths:

```bash
# Run pipeline
python video_pipeline/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --output outputs/result.mp4

# Monitor progress
./video_pipeline/monitor_progress.sh

# View results
vlc outputs/result.mp4

# Read documentation
cat docs/README.md
```

## 📚 Documentation Links

- **Main Index**: [docs/README.md](README.md)
- **Quick Start**: [docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Usage Guide**: [docs/VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md)
- **Results**: [docs/FINAL_RESULTS.md](FINAL_RESULTS.md)

