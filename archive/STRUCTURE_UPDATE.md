# Structure Update Summary

This document summarizes the reorganization of the project structure.

## Changes Made

### Scripts Consolidation
- **Moved from `video_pipeline/` to `scripts/`**:
  - `video_pipeline.py` - Main pipeline script
  - `multi_object_detector.py` - Multi-object detection module
  - `physics_estimator.py` - VLM wrapper module

- **Moved from `video_pipeline/` to `archive/`** (unnecessary scripts):
  - `segment_hand_doorknob.py` - Specialized segmentation script
  - `monitor_progress.sh` - Progress monitoring script
  - `README.md` - Old video_pipeline README

### Result
- All pipeline scripts are now in `scripts/` folder
- Unnecessary/specialized scripts moved to `archive/`
- `video_pipeline/` folder removed (no longer needed)

## Updated Paths

All documentation has been updated to reflect the new structure:

- **Old**: `python video_pipeline/video_pipeline.py`
- **New**: `python scripts/video_pipeline.py`

## Current Structure

```
spatial-understanding-vr/
├── scripts/                    # All scripts (pipeline + utilities)
│   ├── video_pipeline.py      # Main pipeline
│   ├── multi_object_detector.py
│   ├── physics_estimator.py
│   ├── install_sam3.sh
│   ├── install_sam3_windows.ps1
│   ├── verify_setup.ps1
│   ├── crop_video.py
│   └── render_diagrams.py
│
├── docs/                       # Essential documentation only
│   ├── README.md
│   ├── QUICK_REFERENCE.md
│   ├── VIDEO_PIPELINE_USAGE.md
│   ├── VIDEO_POST_PROCESSING_ANALYSIS.md
│   ├── VIDEO_PIPELINE_UML_DIAGRAMS.md
│   └── PROJECT_STRUCTURE.md
│
├── archive/                    # Historical/deprecated files
│   ├── segment_hand_doorknob.py
│   ├── monitor_progress.sh
│   └── ... (historical docs)
│
└── ... (other folders)
```

## Import Compatibility

All imports remain compatible since the modules are now in the same directory:
- `from physics_estimator import PhysicsEstimator`
- `from multi_object_detector import detect_hands_and_object`

These work when running from project root with `python scripts/video_pipeline.py`.
