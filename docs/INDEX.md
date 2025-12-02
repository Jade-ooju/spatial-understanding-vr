# Video Pipeline Documentation Index

Complete documentation for the SAM 3 + VLM Video Pipeline project.

## 📖 Documentation Files

### Getting Started
1. **[README.md](README.md)** - Overview and documentation index
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick start commands and common usage
3. **[VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md)** - Complete usage guide with examples

### Architecture & Design
4. **[VIDEO_PIPELINE_PLAN.md](VIDEO_PIPELINE_PLAN.md)** - Implementation plan, architecture design, and technical details

### Results & Analysis
5. **[FINAL_RESULTS.md](FINAL_RESULTS.md)** - Complete results from test run with timing breakdown
6. **[TIMING_RESULTS.md](TIMING_RESULTS.md)** - Detailed timing analysis and performance metrics
7. **[RESULTS_LOCATION.md](RESULTS_LOCATION.md)** - Where to find output files and how to view results
8. **[TEST_RESULTS.md](TEST_RESULTS.md)** - Initial test results, troubleshooting, and known limitations

## 🗂️ Project Structure

```
spatial-understanding-vr/
├── README.md                    # Main README
├── SAM3_LICENSE                 # SAM 3 license (required)
├── .gitignore                   # Git ignore file
├── video_pipeline/              # Pipeline scripts
│   ├── video_pipeline.py        # Main pipeline script
│   ├── physics_estimator.py     # VLM wrapper class
│   ├── monitor_progress.sh      # Progress monitoring utility
│   └── README.md                # Scripts documentation
│
├── outputs/                     # Results (user creates)
│   └── *.mp4, *.log            # Output videos and logs
│
└── docs/                        # Documentation (this directory)
    ├── README.md                # Overview
    ├── INDEX.md                 # This file
    ├── QUICK_REFERENCE.md       # Quick commands
    ├── VIDEO_PIPELINE_USAGE.md  # Usage guide
    ├── VIDEO_PIPELINE_PLAN.md   # Architecture
    ├── FINAL_RESULTS.md         # Results
    ├── TIMING_RESULTS.md        # Timing analysis
    ├── RESULTS_LOCATION.md      # Output locations
    └── TEST_RESULTS.md          # Test results
```

## 🚀 Quick Start

```bash
# 1. Activate environment
conda activate sam3

# 2. Run pipeline
python video_pipeline/video_pipeline.py \
  --video resources/VR_short.mkv \
  --prompt "spoon" \
  --output outputs/result.mp4

# 3. View results
vlc outputs/result.mp4
```

## 📚 Reading Order

**For first-time users**:
1. Start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. Read [VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md) for detailed usage
3. Check [FINAL_RESULTS.md](FINAL_RESULTS.md) to see example results

**For developers**:
1. Read [VIDEO_PIPELINE_PLAN.md](VIDEO_PIPELINE_PLAN.md) for architecture
2. Review [TIMING_RESULTS.md](TIMING_RESULTS.md) for performance analysis
3. Check [TEST_RESULTS.md](TEST_RESULTS.md) for known issues

**For troubleshooting**:
1. Check [TEST_RESULTS.md](TEST_RESULTS.md) for common issues
2. Review [RESULTS_LOCATION.md](RESULTS_LOCATION.md) for output locations
3. See [VIDEO_PIPELINE_USAGE.md](VIDEO_PIPELINE_USAGE.md) troubleshooting section

## 🔗 Related Files

- **Scripts**: [`video_pipeline/`](../../video_pipeline/)
- **Results**: [`outputs/`](../../outputs/)
- **Main README**: [`README.md`](../../README.md)

