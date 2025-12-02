# Video Pipeline Implementation Plan

## Overview
Create `video_pipeline.py` that integrates SAM 3 (Segment Anything Model 3) and Moondream2 VLM to process VR headset videos, detect objects, extract them with black backgrounds, and analyze physical properties.

## Architecture Design

### 1. Component Overview
- **Video Input Handler**: OpenCV-based video loading and frame extraction
- **SAM 3 Integration**: Session-based video predictor for object segmentation
- **Mask Processing**: Negative masking (black background) for VLM preprocessing
- **VLM Integration**: PhysicsEstimator for material/weight analysis
- **Visualization**: Real-time display with mask contours and VLM results
- **Frame Optimization**: Skip VLM inference on most frames (every 30 frames)

### 2. SAM 3 API Understanding

**Key Findings:**
- SAM 3 uses a **session-based API** (not simple per-frame prediction)
- Workflow:
  1. `start_session(resource_path)` - Load entire video into session
  2. `add_prompt(session_id, frame_idx, text="...")` - Add text prompt on a frame
  3. `propagate_in_video(session_id, ...)` - Propagate tracking through video
  4. Outputs contain: `out_obj_ids`, `out_binary_masks`, `out_probs`, `out_boxes_xywh`

**Challenge:** The session-based API loads the entire video upfront, but we need frame-by-frame processing for real-time visualization.

**Solution Approach:**
- Option A: Use session API but process frames sequentially from propagation results
- Option B: Create a wrapper that mimics simple `predict(frame, text_prompt)` API
- **Chosen: Option A** - Use session API properly but extract frame-by-frame results

### 3. Implementation Strategy

#### 3.1 Video Processing Flow
```
1. Initialize SAM 3 video predictor
2. Load video with OpenCV (for frame-by-frame access)
3. Start SAM 3 session with video path
4. Add text prompt on frame 0
5. Propagate through video (collect all outputs)
6. For each frame:
   a. Get mask from SAM 3 outputs
   b. Apply negative masking (black background)
   c. Run VLM every 30 frames (or on new object detection)
   d. Visualize: green contour + VLM text overlay
   e. Display with cv2.imshow
```

#### 3.2 SAM 3 Integration Details

**Initialization:**
```python
from sam3.model_builder import build_sam3_video_predictor
predictor = build_sam3_video_predictor(gpus_to_use=[])
```

**Session Management:**
- Start session with video path (MP4 or JPEG folder)
- Add text prompt on frame 0
- Propagate to get all frame outputs
- Close session after processing

**Output Processing:**
- Outputs format: `{frame_idx: {"out_obj_ids": [...], "out_binary_masks": [...], ...}}`
- Extract masks per frame
- Handle multiple objects (use highest confidence or largest mask)

#### 3.3 Negative Masking Implementation

**Critical Requirement:** Make background completely BLACK (RGB 0,0,0)

```python
# Pseudo-code
masked_frame = frame.copy()
masked_frame[~mask] = [0, 0, 0]  # Set non-mask pixels to black
```

**Edge Cases:**
- No mask detected: Skip VLM, show raw frame
- Multiple masks: Use primary object (highest score or largest area)

#### 3.4 VLM Integration

**PhysicsEstimator Interface (Assumed):**
```python
from physics_estimator import PhysicsEstimator

estimator = PhysicsEstimator()
result = estimator.analyze(image_with_black_bg)
# Returns: {"material": "...", "weight": "..."}
```

**Optimization Strategy:**
- Run VLM every 30 frames (approximately 1 second at 30 FPS)
- Cache last VLM result
- Re-run if new object detected (track object ID changes)
- Skip if no mask found

#### 3.5 Visualization

**Requirements:**
- Green mask contour (cv2.drawContours)
- VLM result text overlay (cv2.putText)
- Real-time display (cv2.imshow)
- Exit on 'q' key press

**Text Overlay Format:**
```
Material: <material>
Weight: <weight>
```

### 4. Code Structure

```python
video_pipeline.py
├── Imports
│   ├── cv2, torch, numpy
│   ├── sam3.model_builder
│   └── physics_estimator (assumed to exist)
│
├── Helper Functions
│   ├── apply_negative_mask(frame, mask) -> masked_frame
│   ├── extract_primary_mask(outputs, frame_idx) -> mask
│   ├── draw_mask_contour(frame, mask) -> annotated_frame
│   └── overlay_vlm_text(frame, vlm_result) -> annotated_frame
│
├── Main Function: ProcessVideo
│   ├── Initialize SAM 3 predictor
│   ├── Load video with OpenCV
│   ├── Start SAM 3 session
│   ├── Add text prompt
│   ├── Propagate through video
│   ├── Process frames loop:
│   │   ├── Get mask from SAM 3 outputs
│   │   ├── Apply negative masking
│   │   ├── Run VLM (every 30 frames or new object)
│   │   ├── Visualize
│   │   └── Display and handle 'q' key
│   └── Cleanup (close session, release video)
│
└── Main Entry Point
    └── if __name__ == "__main__": ProcessVideo(...)
```

### 5. Edge Cases & Error Handling

1. **No mask detected:**
   - Skip VLM inference
   - Show raw frame without annotations
   - Continue to next frame

2. **Multiple objects detected:**
   - Use object with highest confidence score
   - Or largest mask area
   - Log warning if multiple objects found

3. **Video loading failure:**
   - Check file exists
   - Validate video format
   - Provide clear error message

4. **SAM 3 session errors:**
   - Handle session timeout
   - Graceful cleanup on errors
   - Resource deallocation

5. **VLM errors:**
   - Try-except around VLM calls
   - Use cached result if VLM fails
   - Log errors but continue processing

6. **Display errors:**
   - Handle window close events
   - Graceful exit on Ctrl+C

### 6. Environment Considerations

**Conda Environment:**
- Ensure `sam3` conda environment is activated
- Check for required dependencies:
  - `opencv-python`
  - `torch`
  - `numpy`
  - SAM 3 package (installed via `pip install -e .`)

**Environment Check Function:**
```python
def check_environment():
    """Verify conda environment and dependencies"""
    import sys
    import os
    
    # Check if in sam3 conda environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    if 'sam3' not in conda_env:
        print("WARNING: Not in 'sam3' conda environment!")
        print(f"Current environment: {conda_env}")
        print("Please activate: conda activate sam3")
    
    # Check critical imports
    try:
        from sam3.model_builder import build_sam3_video_predictor
        print("✓ SAM 3 import successful")
    except ImportError as e:
        print(f"✗ SAM 3 import failed: {e}")
        raise
    
    try:
        from physics_estimator import PhysicsEstimator
        print("✓ PhysicsEstimator import successful")
    except ImportError as e:
        print(f"✗ PhysicsEstimator import failed: {e}")
        print("  Make sure physics_estimator.py exists in the same directory")
        raise
```

### 7. Performance Considerations

1. **Memory Management:**
   - SAM 3 loads entire video into memory (session-based)
   - For very long videos, consider chunking
   - Release video capture after loading frames

2. **GPU Usage:**
   - SAM 3 automatically uses GPU if available
   - Falls back to CPU if CUDA not compatible
   - Monitor GPU memory usage

3. **Frame Processing Speed:**
   - VLM skipping (every 30 frames) is critical
   - Mask extraction is fast (numpy operations)
   - Visualization overhead is minimal

### 8. Testing Strategy

1. **Unit Tests:**
   - Negative masking function
   - Mask extraction from SAM 3 outputs
   - Frame skipping logic

2. **Integration Tests:**
   - End-to-end with sample video
   - Error handling scenarios
   - Edge cases (no mask, multiple objects)

3. **Manual Testing:**
   - Test with VR headset video
   - Verify visualization quality
   - Check VLM result accuracy

### 9. Dependencies

**Required:**
- `opencv-python` (video handling)
- `torch` (tensor operations)
- `numpy` (array operations)
- `sam3` (SAM 3 model - installed via pip install -e .)
- `physics_estimator.py` (assumed to exist in same directory)

**Optional:**
- `tqdm` (progress bars)
- `logging` (debugging)

### 10. Implementation Checklist

- [ ] Create `video_pipeline.py` file structure
- [ ] Implement environment check function
- [ ] Implement SAM 3 predictor initialization
- [ ] Implement video loading with OpenCV
- [ ] Implement SAM 3 session management
- [ ] Implement mask extraction from SAM 3 outputs
- [ ] Implement negative masking function
- [ ] Implement VLM integration with frame skipping
- [ ] Implement visualization functions
- [ ] Implement main ProcessVideo function
- [ ] Add error handling and edge cases
- [ ] Add command-line argument parsing
- [ ] Test with sample video
- [ ] Document usage and parameters

### 11. API Design Decisions

**Function Signature:**
```python
def ProcessVideo(
    video_path: str,
    text_prompt: str = "cup",
    vlm_interval: int = 30,
    display: bool = True,
    output_path: Optional[str] = None
) -> None:
    """
    Process video with SAM 3 and VLM analysis.
    
    Args:
        video_path: Path to video file (MP4) or JPEG folder
        text_prompt: Text prompt for SAM 3 (e.g., "cup", "handle")
        vlm_interval: Run VLM every N frames (default: 30)
        display: Show real-time visualization (default: True)
        output_path: Optional path to save annotated video
    """
```

**Command-Line Interface:**
```bash
python video_pipeline.py --video path/to/video.mp4 --prompt "cup" --vlm-interval 30
```

### 12. Notes on SAM 3 Session API

**Important:** SAM 3's session-based API is designed for batch processing of entire videos, not real-time frame-by-frame processing. However, we can:

1. Start session and propagate once to get all masks
2. Then process frames sequentially for visualization
3. This approach works well for post-processing scenarios

**Alternative for Real-Time:** If real-time processing is needed, would need to:
- Use SAM 3 image predictor per frame (slower, no tracking)
- Or implement custom frame-by-frame session management

For this use case (VR video analysis), batch processing is acceptable.

## Next Steps

1. Review and approve this plan
2. Implement core functions incrementally
3. Test with sample video
4. Refine based on results
5. Add documentation and examples

