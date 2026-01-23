# Project Structure

This document describes the organization and structure of the Spatial Understanding for VR project.

## Directory Structure

```
spatial-understanding-vr/
│
├── Root Files
│ ├── README.md # Main project README
│ ├── SAM3_LICENSE # SAM 3 license file
│ └── .gitignore # Git ignore rules
│
├── scripts/ # All Scripts (Pipeline + Utilities)
│ ├── video_pipeline.py # Main pipeline orchestrator
│ ├── multi_object_detector.py # Multi-object detection module
│ ├── physics_estimator.py # VLM-based physics estimation
│ ├── install_sam3.sh # SAM 3 installation (Linux)
│ ├── install_sam3_windows.ps1 # SAM 3 installation (Windows)
│ ├── verify_setup.ps1 # Setup verification (Windows)
│ ├── crop_video.py # Video preprocessing utility
│ └── render_diagrams.py # Diagram rendering utility
│
├── docs/ # Documentation
│ ├── README.md # Documentation index
│ ├── QUICK_REFERENCE.md # Quick reference
│ ├── VIDEO_PIPELINE_USAGE.md # Usage guide
│ ├── VIDEO_POST_PROCESSING_ANALYSIS.md # Complete pipeline analysis
│ ├── SETUP.md # GitHub repository setup (optional)
│ ├── SETUP_WINDOWS.md # Windows setup guide
│ └── PROJECT_STRUCTURE.md # Project organization
│
├── diagrams/ # Rendered UML Diagrams
│ ├── high_level_overview.png # High-level overview (PNG)
│ ├── high_level_overview.svg # High-level overview (SVG)
│ ├── pipeline_flow.png # Pipeline flow (PNG)
│ ├── pipeline_flow.svg # Pipeline flow (SVG)
│ ├── component_diagram.png # Component diagram
│ ├── sequence_diagram.png # Sequence diagram
│ ├── activity_diagram.png # Activity diagram
│ ├── class_diagram.png # Class diagram
│ ├── data_flow_diagram.png # Data flow diagram
│ ├── state_diagram.png # State diagram
│ ├── package_diagram.png # Package diagram
│ ├── interaction_overview_diagram.png # Interaction overview
│ ├── HIGH_QUALITY_DIAGRAMS.md # Diagram guide
│ ├── README.md # Diagrams README
│ └── *.mmd # Mermaid source files
│
├── tests/ # Test Scripts
│ ├── test_my_vr_image.py # VR image test
│ ├── test_ar_hud.py # AR HUD test
│ └── README.md # Test documentation
│
├── archive/ # Historical/Deprecated Files
│ ├── README.md # Archive documentation
│ ├── segment_hand_doorknob.py # Specialized segmentation (deprecated)
│ ├── monitor_progress.sh # Progress monitoring (deprecated)
│ ├── ARCHIVED_DOCS_README.md # Archived documentation index
│ ├── FINAL_RESULTS.md # Historical test results
│ ├── FULL_VIDEO_TEST_REPORT.md # Historical test reports
│ ├── TEST_PIPELINE.md # Historical test documentation
│ └── ... # Other historical files
│
└── resources/ # Input Resources (not in git)
 └── README.md # Resources documentation
```

## File Categories

### Core Code
- **`scripts/`**: All pipeline and utility scripts
 - `video_pipeline.py`: Main orchestrator
 - `multi_object_detector.py`: Object detection
 - `physics_estimator.py`: VLM integration

### Documentation
- **`docs/`**: All project documentation
 - Architecture and analysis documents
 - Usage guides and quick references
 - Test results and reports
 - Setup and installation guides

### Visual Documentation
- **`diagrams/`**: Rendered UML diagrams
 - High-quality PNG and SVG files
 - Mermaid source files (`.mmd`)
 - Diagram guides and documentation

### Scripts
- **`scripts/`**: All scripts (pipeline and utilities)
 - Pipeline scripts (video_pipeline.py, multi_object_detector.py, physics_estimator.py)
 - Installation scripts
 - Setup verification
 - Video preprocessing
 - Diagram rendering

### Testing
- **`tests/`**: Test scripts and documentation
 - Unit tests
 - Integration tests
 - Test documentation

### Archive
- **`archive/`**: Historical and deprecated files
 - Old documentation
 - Deprecated scripts
 - Migration notes

## Organization Principles

1. **Separation of Concerns**
 - All scripts in `scripts/`
 - Documentation in `docs/`
 - Tests in `tests/`
 - Historical files in `archive/`

2. **Clear Documentation Structure**
 - Main README at root
 - Detailed docs in `docs/`
 - Visual docs in `diagrams/`

3. **Platform Support**
 - Platform-specific scripts clearly labeled
 - Both Windows and Linux support

4. **Historical Preservation**
 - Old files moved to `archive/` not deleted
 - Clear documentation of what's archived

## File Naming Conventions

- **Documentation**: `UPPER_CASE.md` for major docs, `lower_case.md` for specific topics
- **Scripts**: `snake_case.py` or `kebab-case.sh`
- **Diagrams**: `descriptive_name.png/svg`
- **Tests**: `test_*.py`

## Maintenance

- **Regular Cleanup**: Move deprecated files to `archive/`
- **Documentation Updates**: Keep docs in sync with code changes
- **Structure Reviews**: Periodically review and optimize structure

## Related Documentation

- [Main README](../README.md) - Project overview
- [Documentation Index](README.md) - Complete documentation list
- [Archive README](../archive/README.md) - Archive contents
