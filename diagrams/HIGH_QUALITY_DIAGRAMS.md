# High-Quality Pipeline Diagrams

This document provides high-quality, readable diagrams of the video post-processing pipeline with key information.

## Recommended Diagrams (High Quality)

### 1. High-Level Overview
**File**: `high_level_overview.png` / `high_level_overview.svg`

**Purpose**: Shows the complete pipeline from input to output in a clear, readable format.

**Key Information**:
- **Input**: Video file (MP4/MKV) + Text prompt (e.g., 'spoon')
- **Pipeline Components**: 
 - Video Pipeline (Main Orchestrator)
 - Multi-Object Detector (Hands + Objects)
 - Physics Estimator (VLM Analysis)
- **Processing Stages**:
 1. Detection (SAM 3 Sessions)
 2. Mask Extraction (Frame-indexed)
 3. VLM Analysis (Every 30 frames)
 4. Visualization (Masks + AR HUD)
- **Output**: Real-time Display + Annotated Video

**Use Case**: Best for presentations, overview documentation, and understanding the big picture.

---

### 2. Pipeline Flow Diagram
**File**: `pipeline_flow.png` / `pipeline_flow.svg`

**Purpose**: Shows the detailed step-by-step flow of video processing.

**Key Information**:
- **Initialization**: SAM 3 + VLM setup
- **Detection Phase**: 
 - Session 1: Detect Hands
 - Session 2: Detect Objects
- **Frame Processing Loop**:
 - Read frame → Get masks → VLM analysis (every 30 frames) → Visualize → Display/Write
- **Visualization Steps**:
 - Color Masks (Cyan/Green)
 - Contours
 - Wireframes
 - AR HUD Overlays

**Use Case**: Best for understanding the detailed workflow and decision points.

---

## Important Pipeline Information

### Core Architecture

1. **Two-Stage Detection**
 - **Session 1**: Hand detection using SAM 3 with prompt "hand"
 - **Session 2**: Object detection using SAM 3 with custom prompt (e.g., "spoon")
 - Both sessions run independently and store results in frame-indexed dictionaries

2. **VLM Optimization**
 - VLM (Vision Language Model) analysis runs **every 30 frames** (not every frame)
 - Results are cached and reused for intermediate frames
 - Analyzes: Material, Weight, Situation

3. **Visualization Pipeline**
 - Color-coded masks: Cyan for hands, Green for objects
 - 2D wireframes for spatial representation
 - AR HUD overlays with context (material, weight) and action labels

4. **Output Options**
 - Real-time display via OpenCV window
 - Annotated video output (MP4 format)
 - Both can be enabled simultaneously

### Key Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Video Pipeline** | Main orchestrator | Coordinates all processing steps |
| **Multi-Object Detector** | Object segmentation | Separate SAM 3 sessions for hands and objects |
| **Physics Estimator** | Physical property analysis | VLM-based (Moondream2) with placeholder fallback |
| **SAM 3** | Segmentation model | Session-based API, processes entire video |
| **OpenCV** | Video I/O & Visualization | Frame reading, display, video writing |

### Processing Flow Summary

```
1. Initialize (SAM 3 + VLM)
 ↓
2. Load Video (OpenCV)
 ↓
3. Multi-Object Detection
 ├─ Session 1: Hands → hands_masks dict
 └─ Session 2: Objects → object_masks dict
 ↓
4. Frame-by-Frame Processing
 ├─ Get masks for frame
 ├─ VLM analysis (every 30 frames)
 ├─ Visualization (masks, contours, wireframes, HUD)
 └─ Display/Write frame
 ↓
5. Output (Display + Annotated Video)
```

### Performance Characteristics

- **VLM Optimization**: Runs every 30 frames (~1 second at 30 FPS)
- **Batch Processing**: SAM 3 processes entire video in one session
- **Memory**: Stores frame-indexed mask dictionaries
- **GPU Support**: Automatic GPU usage for SAM 3 if available

---

## All Available Diagrams

### High-Quality Simplified (Recommended)
- `high_level_overview.png` / `.svg` - **Best for overview**
- `pipeline_flow.png` / `.svg` - **Best for detailed flow**

### Detailed Technical Diagrams
- `component_diagram.png` / `.svg` - System architecture
- `sequence_diagram.png` / `.svg` - Component interactions
- `activity_diagram.png` / `.svg` - Detailed workflow
- `class_diagram.png` / `.svg` - Class structure
- `data_flow_diagram.png` / `.svg` - Data flow
- `state_diagram.png` / `.svg` - State transitions
- `package_diagram.png` / `.svg` - Module organization
- `interaction_overview_diagram.png` / `.svg` - Interaction summary

---

## Usage Tips

1. **For Presentations**: Use `high_level_overview.png` (2400x1800, high DPI)
2. **For Documentation**: Use SVG files for best quality and scalability
3. **For Understanding Flow**: Use `pipeline_flow.png` for step-by-step process
4. **For Technical Details**: Refer to detailed diagrams in `VIDEO_PIPELINE_UML_DIAGRAMS.md`

---

## Regenerating Diagrams

To regenerate all diagrams with high quality:

```bash
python render_diagrams.py
```

The script now uses:
- **PNG**: 2400x1800 resolution with 2x scale factor
- **SVG**: Vector format (always high quality)

---

## Notes

- All PNG files are rendered at **2400x1800 pixels** with **2x scale factor** for crisp text
- SVG files are vector-based and scale perfectly to any size
- Diagrams use color coding for easy identification of components
- Text is optimized for readability at high resolutions
