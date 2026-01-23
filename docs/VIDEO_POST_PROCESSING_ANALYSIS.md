# Video Post-Processing Pipeline Analysis

## Executive Summary

The video post-processing pipeline in `spatial-understanding-vr` is a system that processes VR headset videos to segment objects, analyze physical properties, and generate annotated visualizations. The pipeline integrates SAM 3 (Segment Anything Model 3) for object segmentation and a VLM (Vision Language Model) for physical property estimation.

## Architecture Overview

### Core Components

1. **Main Pipeline** (`video_pipeline.py`)
   - Orchestrates the entire processing workflow
   - Handles video I/O, visualization, and user interaction
   - Integrates all sub-components

2. **Multi-Object Detector** (`multi_object_detector.py`)
   - Detects hands and target objects separately using SAM 3
   - Uses separate SAM 3 sessions for each object type
   - Returns frame-indexed mask dictionaries

3. **Physics Estimator** (`physics_estimator.py`)
   - VLM-based physical property analysis
   - Estimates material, weight, and situation
   - Supports Moondream2 integration (with placeholder fallback)

4. **Specialized Segmentation** (`segment_hand_doorknob.py`)
   - Specialized script for hand + door knob segmentation
   - Can process single images or videos
   - Provides visualization with color-coded masks

## Pipeline Flow

### Phase 1: Initialization
```
1. Environment Check
   ├── Verify conda environment (sam3)
   ├── Check CUDA availability
   └── Validate dependencies

2. Model Initialization
   ├── Initialize SAM 3 video predictor
   │   └── GPU/CPU selection (prefers GPU)
   └── Initialize PhysicsEstimator (VLM)
       └── Moondream2 or placeholder mode
```

### Phase 2: Video Loading & Analysis
```
3. Video Input
   ├── Open video with OpenCV
   ├── Extract metadata (FPS, dimensions, frame count)
   └── Validate video format

4. Multi-Object Detection (SAM 3)
   ├── Session 1: Hand Detection
   │   ├── Start SAM 3 session with video path
   │   ├── Add text prompt "hand" on frame 0
   │   ├── Propagate tracking through video
   │   └── Extract masks per frame → hands_masks dict
   │
   └── Session 2: Target Object Detection
       ├── Start new SAM 3 session
       ├── Add object text prompt (e.g., "spoon") on frame 0
       ├── Propagate tracking through video
       └── Extract masks per frame → object_masks dict
```

### Phase 3: Frame-by-Frame Processing
```
5. Frame Processing Loop
   For each frame:
   ├── Read frame from video (OpenCV)
   ├── Get masks for current frame
   │   ├── hand_mask = hands_masks[frame_count]
   │   └── object_mask = object_masks[frame_count]
   │
   ├── VLM Analysis (every N frames, default: 30)
   │   ├── Select mask (prefer object over hand)
   │   ├── Apply negative masking (black background)
   │   ├── Run PhysicsEstimator.analyze()
   │   └── Cache result for subsequent frames
   │
   ├── Visualization
   │   ├── Apply color masks (cyan for hands, green for object)
   │   ├── Draw contours
   │   ├── Draw 2D wireframes
   │   ├── Draw AR HUD overlays:
   │   │   ├── Context block (top-right): material, weight, object name
   │   │   └── Action label (top-left): action verb and state
   │   └── Optional: 3D bounding box wireframe
   │
   ├── Display/Output
   │   ├── Show in OpenCV window (if display=True)
   │   ├── Write to output video (if output_path specified)
   │   └── Handle user input ('q' quit, 'p' pause)
   │
   └── Frame counter increment
```

### Phase 4: Cleanup
```
6. Finalization
   ├── Release video writer
   ├── Close OpenCV windows
   ├── Release video capture
   └── Print timing statistics
```

## Key Processing Functions

### 1. Negative Masking (`apply_negative_mask`)
**Purpose**: Create black background for VLM analysis
```python
def apply_negative_mask(frame: np.ndarray, mask: np.ndarray) -> np.ndarray:
    # Sets all non-mask pixels to black (RGB 0,0,0)
    masked_frame = frame.copy()
    masked_frame[~mask] = [0, 0, 0]
    return masked_frame
```

**Usage**: Applied before VLM analysis to isolate object from background

### 2. Mask Extraction (`extract_primary_mask`)
**Purpose**: Extract primary mask from SAM 3 outputs
- Handles multiple masks per frame
- Selects highest confidence or largest area
- Converts tensors to numpy arrays
- Ensures boolean mask format

### 3. Multi-Object Detection (`detect_hands_and_object`)
**Purpose**: Detect both hands and target object in parallel sessions
- **Session 1**: Hand detection with prompt "hand"
- **Session 2**: Object detection with custom prompt
- Returns: `{"hands": {frame_idx: mask}, "object": {frame_idx: mask}}`

### 4. VLM Analysis (`PhysicsEstimator.analyze`)
**Purpose**: Estimate physical properties
- **Input**: RGB image with black background
- **Output**: `{"material": str, "weight": str, "situation": str}`
- **Optimization**: Runs every N frames (default: 30), caches results

### 5. Visualization Functions
- `visualize_multi_object_masks`: Color-coded mask overlays
- `draw_mask_contour`: Green/cyan contour lines
- `draw_wireframe_2d`: Sparse wireframe representation
- `draw_context_block`: AR HUD metadata display
- `draw_action_label`: Action/state information

## Data Flow

```
Video File (MP4/MKV)
    ↓
OpenCV VideoCapture
    ↓
┌─────────────────────────────────────┐
│  SAM 3 Session 1: Hand Detection    │
│  ┌───────────────────────────────┐   │
│  │ start_session(video_path)     │   │
│  │ add_prompt("hand", frame=0)   │   │
│  │ propagate_in_video()          │   │
│  └───────────────────────────────┘   │
│  → hands_masks: {frame: mask}        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  SAM 3 Session 2: Object Detection  │
│  ┌───────────────────────────────┐   │
│  │ start_session(video_path)     │   │
│  │ add_prompt(object, frame=0)   │   │
│  │ propagate_in_video()          │   │
│  └───────────────────────────────┘   │
│  → object_masks: {frame: mask}       │
└─────────────────────────────────────┘
    ↓
Frame-by-Frame Processing Loop
    ↓
┌─────────────────────────────────────┐
│  For each frame:                     │
│  ├─ Get masks (hands + object)      │
│  ├─ Apply negative masking           │
│  ├─ VLM analysis (every 30 frames)   │
│  ├─ Visualization                    │
│  └─ Display/Write                    │
└─────────────────────────────────────┘
    ↓
Annotated Video Output
```

## Performance Characteristics

### Processing Speed
- **SAM 3 Propagation**: Batch processing of entire video (session-based)
- **VLM Analysis**: Optimized to run every 30 frames (~1 second at 30 FPS)
- **Frame Processing**: Fast (numpy operations, minimal overhead)
- **Visualization**: Minimal overhead (OpenCV operations)

### Memory Usage
- **SAM 3**: Loads entire video into memory (session-based API)
- **Masks Storage**: Two dictionaries (hands + object) with frame-indexed masks
- **Frame Buffers**: Single frame in memory at a time during processing

### Optimization Strategies
1. **VLM Frame Skipping**: Default interval of 30 frames reduces VLM calls by 97%
2. **Result Caching**: Last VLM result reused for intermediate frames
3. **GPU Acceleration**: Automatic GPU usage for SAM 3 if available
4. **Batch Processing**: SAM 3 processes entire video in one session

## Configuration Options

### Command-Line Arguments
- `--video`: Input video path (required)
- `--prompt`: Text prompt for object detection (default: "spoon")
- `--vlm-interval`: VLM analysis frequency in frames (default: 30)
- `--no-display`: Disable real-time display (headless mode)
- `--output`: Path to save annotated video
- `--max-frames`: Limit processing to first N frames (testing)

### Visualization Options
- **Hand Color**: Cyan (255, 255, 0) in BGR
- **Object Color**: Green (0, 255, 0) in BGR
- **Wireframe Color**: White (255, 255, 255) in BGR
- **Mask Alpha**: 0.4 (semi-transparent overlay)
- **Contour Thickness**: 2 pixels

## Error Handling

### Robustness Features
1. **Missing Masks**: Gracefully handles frames without detections
2. **VLM Failures**: Falls back to cached results or placeholder mode
3. **Session Errors**: Continues with empty masks if detection fails
4. **Video I/O Errors**: Validates file existence and format
5. **Display Errors**: Handles window close events gracefully

### Edge Cases Handled
- No mask detected: Skip VLM, show raw frame
- Multiple objects: Select highest confidence or largest area
- VLM unavailable: Use placeholder heuristics
- GPU unavailable: Fall back to CPU
- Very long videos: Optional frame limiting

## Dependencies

### Required
- **SAM 3**: Video segmentation model (installed via pip)
- **OpenCV**: Video I/O and visualization (`opencv-python`)
- **PyTorch**: Tensor operations and model inference
- **NumPy**: Array operations
- **Moondream2**: VLM for physical property analysis
  - Install: `pip install transformers torch`
  - Falls back to placeholder if unavailable

### Environment
- **Conda Environment**: `sam3` (required)
- **CUDA**: Optional but recommended for GPU acceleration

## Output Formats

### Visual Output
- **Real-time Display**: OpenCV window with annotated frames
- **Video File**: MP4 format with all annotations
- **Annotations Include**:
  - Color-coded mask overlays (hands: cyan, object: green)
  - Contour lines
  - 2D wireframes
  - AR HUD overlays (context block, action label)

### Metadata Output
- **Console Logging**: Processing progress and timing
- **VLM Results**: Material, weight, situation per analysis frame
- **Statistics**: Frame count, FPS, VLM timing

## Usage Examples

### Basic Usage
```bash
python scripts/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon"
```

### With Output Video
```bash
python scripts/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --output outputs/annotated.mp4
```

### Headless Processing
```bash
python scripts/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --no-display \
  --output outputs/annotated.mp4
```

### Testing (Limited Frames)
```bash
python scripts/video_pipeline.py \
  --video resources/VR.mkv \
  --prompt "spoon" \
  --max-frames 100
```

## Potential Improvements

1. **Memory Efficiency**: 
   - Current: Loads entire video into memory (SAM 3 session-based)
   - Improvement: Chunk-based processing for very long videos

2. **VLM Integration**:
   - Current: Placeholder mode when Moondream2 unavailable
   - Improvement: Complete Moondream2 API integration

3. **Real-time Processing**:
   - Current: Post-processing pipeline (batch mode)
   - Improvement: Frame-by-frame streaming for real-time applications

4. **Mask Refinement**:
   - Current: Uses primary mask (highest confidence)
   - Improvement: Multi-object tracking with ID persistence

5. **Output Formats**:
   - Current: MP4 video only
   - Improvement: JSON metadata export, frame-by-frame mask export

## Related Scripts

### `segment_hand_doorknob.py`
- Specialized version for hand + door knob segmentation
- Can process single images or videos
- Simpler visualization (no VLM analysis)
- Useful for specific use cases

### `crop_video.py`
- Utility script for video preprocessing
- Not part of main pipeline but used for preparation
