# Visualization Implementation Plan - Day 11-13

## Overview
Implement video visualization with:
- **SAM 3 fluorescent color masks** for target objects and hands
- **VLM information overlay** (weight, material, situation)
- **3D wireframe** visualization

## Current Status
✅ **Completed (Day 8-9):**
- SAM 3 extracts masked images
- Moondream2 VLM analyzes material/weight from masked images

📋 **Current Pipeline:**
- Basic green contour visualization
- Simple text overlay (Material, Weight)
- No hand detection
- No color masking
- No 3D wireframe
- No situation description

## Videos Available
- `Resources/Recording/MR_View/Egg_001.mp4` - Pick and place an egg
- `Resources/Recording/MR_View/Egg_002.mp4` - Pick and place an egg
- `Resources/Recording/MR_View/Power_001.mp4` - Lift heavy dumbbell
- `Resources/Recording/MR_View/Power_002.mp4` - Lift heavy dumbbell

---

## Task Breakdown

### Task 1: Enhance VLM Analysis (Finetune/Improve Prompts)

#### 1.1 Current VLM Implementation
**File:** `video_pipeline/physics_estimator.py`

**Current prompts:**
- Material: "What material is this object made of? Answer in one word or short phrase."
- Weight: "Estimate the weight of this object. Answer in one word or short phrase like 'light', 'medium', 'heavy', or specific weight if possible."

**Current output:**
```python
{
    "material": "...",
    "weight": "..."
}
```

#### 1.2 Required Enhancements

**A. Add "Situation" Analysis**
- **Goal:** Describe what's happening in the scene (interaction context)
- **Prompt:** "Describe what is happening with this object. Is it being picked up, held, placed, lifted? Answer in one short sentence."
- **Example outputs:**
  - "Being picked up by hand"
  - "Held in hand"
  - "Being lifted with effort"
  - "Placed on surface"

**B. Improve Weight Estimation**
- **Current:** Generic "light/medium/heavy"
- **Target:** More specific estimates
  - For eggs: "~50-60g" or "light (50-60g)"
  - For dumbbells: "~5-10kg" or "heavy (5-10kg)"
- **Enhanced prompt:** "Estimate the weight of this object in grams or kilograms. If you can't be specific, use 'light' (<100g), 'medium' (100g-1kg), or 'heavy' (>1kg)."

**C. Improve Material Detection**
- **Current:** Basic material detection
- **Target:** More specific materials
  - Eggs: "ceramic" or "porcelain" (if applicable)
  - Dumbbells: "metal" or "steel"
- **Enhanced prompt:** "What material is this object made of? Be specific (e.g., 'ceramic', 'metal', 'plastic', 'wood')."

#### 1.3 Implementation Steps

**Step 1.1:** Update `PhysicsEstimator.analyze()` method
- Add situation prompt
- Improve weight and material prompts
- Return dictionary with: `{"material": ..., "weight": ..., "situation": ...}`

**Step 1.2:** Update `overlay_vlm_text()` function
- Add situation text line
- Format: 3 lines instead of 2
- Position: Adjust layout to fit 3 lines

**Step 1.3:** Test with sample frames
- Test with egg images (should detect "ceramic/porcelain", "light", "being picked up")
- Test with dumbbell images (should detect "metal", "heavy", "being lifted")

**Files to modify:**
- `video_pipeline/physics_estimator.py` - Add situation analysis
- `video_pipeline/video_pipeline.py` - Update text overlay function

---

### Task 2: SAM 3 Multi-Object Detection (Hands + Target Object)

#### 2.1 Current Implementation
**Current:** Single object detection with text prompt (e.g., "spoon", "egg", "dumbbell")

**Limitation:** Only detects one object type at a time

#### 2.2 Required Enhancements

**A. Detect Hands**
- **Goal:** Identify and mask hands in the video
- **Approach:** Use SAM 3 with text prompt "hand" or "hands"
- **Challenge:** Need to run SAM 3 twice (once for target object, once for hands)
- **Solution:** Run two separate SAM 3 sessions OR use multiple prompts in one session

**B. Detect Target Object**
- **Goal:** Identify the interaction target (egg, dumbbell, etc.)
- **Current:** Already working with text prompts
- **Enhancement:** Ensure we get the correct object (not background)

**C. Track Both Objects**
- **Goal:** Track hands and target object simultaneously through video
- **Approach:** 
  - Option A: Two separate SAM 3 sessions (one for hands, one for target)
  - Option B: Use SAM 3's multi-object tracking (if supported)
  - **Recommended:** Option A (simpler, more reliable)

#### 2.3 Implementation Steps

**Step 2.1:** Create multi-object detection function
- Function: `detect_hands_and_object(video_path, object_prompt)`
- Returns: `{"hands": {frame_idx: mask}, "object": {frame_idx: mask}}`
- Run SAM 3 twice:
  1. Session 1: Prompt "hand" or "hands" → get hand masks
  2. Session 2: Prompt object_prompt → get object masks

**Step 2.2:** Update `ProcessVideo()` function
- Accept both hand and object masks
- Process both masks in visualization

**Step 2.3:** Handle edge cases
- No hands detected: Only show object mask
- No object detected: Only show hand mask
- Both detected: Show both with different colors

**Files to create/modify:**
- `video_pipeline/video_pipeline.py` - Add multi-object detection
- Consider: `video_pipeline/multi_object_detector.py` (new file for cleaner code)

---

### Task 3: Color Mask Visualization (Fluorescent Masks)

#### 3.1 Current Implementation
**Current:** Green contour only (`draw_mask_contour()`)

**Limitation:** Only shows outline, not filled mask

#### 3.2 Required Enhancements

**A. Fluorescent Color Masks**
- **Goal:** Fill mask areas with semi-transparent fluorescent colors
- **Colors:**
  - **Hands:** Cyan/Blue fluorescent (`(255, 255, 0)` in BGR or `(0, 255, 255)` in RGB)
  - **Target Object:** Green/Magenta fluorescent (`(0, 255, 0)` in BGR or `(255, 0, 255)` in RGB)
- **Style:** Semi-transparent overlay (alpha blending)
- **Reference:** Similar to SAM 3's `render_masklet_frame()` function

**B. Mask Overlay Implementation**
- Use `cv2.addWeighted()` for alpha blending
- Alpha value: 0.3-0.5 (adjustable)
- Keep original image visible underneath

**C. Contour Enhancement**
- Keep contour lines for clarity
- Different colors for hands vs object
- Thicker lines for better visibility

#### 3.3 Implementation Steps

**Step 3.1:** Create `apply_color_mask()` function
- Input: frame, mask, color (BGR), alpha
- Output: frame with colored mask overlay
- Use: `cv2.addWeighted()` for blending

**Step 3.2:** Create `visualize_multi_object_masks()` function
- Input: frame, hand_mask, object_mask
- Output: frame with both masks overlaid
- Colors:
  - Hands: Cyan (`(255, 255, 0)` BGR)
  - Object: Green (`(0, 255, 0)` BGR) or Magenta (`(255, 0, 255)` BGR)

**Step 3.3:** Update main processing loop
- Apply color masks instead of just contours
- Keep contours for edge definition

**Files to modify:**
- `video_pipeline/video_pipeline.py` - Add color mask functions

---

### Task 4: 3D Wireframe Visualization

#### 4.1 Goal
Overlay 3D wireframe representation of detected objects on video frames.

#### 4.2 Approach Options

**Option A: Simple 2D Wireframe (Easier)**
- Extract object contour from mask
- Draw wireframe-like lines connecting contour points
- Use `cv2.drawContours()` with specific style
- **Pros:** Simple, fast, no 3D reconstruction needed
- **Cons:** Not true 3D, just 2D outline

**Option B: 3D Mesh Reconstruction (Advanced)**
- Use depth information (if available from MR headset)
- Reconstruct 3D mesh from mask + depth
- Project 3D wireframe back to 2D
- **Pros:** True 3D representation
- **Cons:** Requires depth data, more complex

**Option C: Estimated 3D Wireframe (Medium)**
- Use mask to estimate object shape
- Create simple 3D bounding box or ellipsoid
- Project to 2D for overlay
- **Pros:** Gives 3D feel without depth data
- **Cons:** Estimated, not accurate

#### 4.3 Recommended: Option A (Simple 2D Wireframe) + Option C (Estimated 3D)

**Phase 1:** Implement simple 2D wireframe
- Extract contour from mask
- Draw wireframe-style lines (sparse, not filled)
- Use different line styles for hands vs object

**Phase 2 (Optional):** Add estimated 3D bounding box
- Calculate 3D bounding box from mask (assuming depth = estimated from size)
- Project corners to 2D
- Draw wireframe box

#### 4.4 Implementation Steps

**Step 4.1:** Create `draw_wireframe_2d()` function
- Input: frame, mask, color, line_thickness
- Extract contour points
- Draw sparse wireframe lines (every Nth point)
- Style: Dashed or dotted lines

**Step 4.2:** Create `draw_estimated_3d_box()` function (optional)
- Input: frame, mask, color
- Calculate bounding box from mask
- Estimate depth from mask area
- Project 3D box corners to 2D
- Draw wireframe box

**Step 4.3:** Integrate into visualization
- Add wireframe overlay after color masks
- Use different styles for hands vs object

**Files to create/modify:**
- `video_pipeline/video_pipeline.py` - Add wireframe functions
- Consider: `video_pipeline/wireframe_utils.py` (new file)

---

## Implementation Priority

### Phase 1: Core Visualization (Days 11-12)
1. ✅ **Task 1:** Enhance VLM (add situation, improve prompts)
2. ✅ **Task 2:** Multi-object detection (hands + target)
3. ✅ **Task 3:** Color mask visualization (fluorescent masks)

### Phase 2: Advanced Visualization (Day 13)
4. ✅ **Task 4:** 3D wireframe (start with simple 2D wireframe)

---

## File Structure

```
spatial-understanding-vr/
├── video_pipeline/
│   ├── video_pipeline.py          # Main pipeline (MODIFY)
│   ├── physics_estimator.py       # VLM integration (MODIFY)
│   ├── multi_object_detector.py   # NEW: Multi-object detection
│   └── wireframe_utils.py         # NEW: Wireframe visualization
├── Resources/
│   └── Recording/
│       └── MR_View/
│           ├── Egg_001.mp4
│           ├── Egg_002.mp4
│           ├── Power_001.mp4
│           └── Power_002.mp4
└── outputs/
    └── [output videos with visualization]
```

---

## Testing Strategy

### Test Videos
1. **Egg videos:** Test hand + egg detection, material="ceramic", weight="light", situation="being picked up"
2. **Dumbbell videos:** Test hand + dumbbell detection, material="metal", weight="heavy", situation="being lifted"

### Validation Checklist
- [ ] VLM returns material, weight, situation
- [ ] Hands are detected and masked
- [ ] Target object is detected and masked
- [ ] Color masks are visible (fluorescent colors)
- [ ] VLM text overlay shows all 3 fields
- [ ] Wireframe is visible (2D or 3D)
- [ ] Visualization runs smoothly (no lag)
- [ ] Output video is saved correctly

---

## Code Examples

### Example 1: Enhanced VLM Analysis
```python
# In physics_estimator.py
def analyze(self, image: np.ndarray) -> Dict[str, str]:
    material_prompt = "What material is this object made of? Be specific (e.g., 'ceramic', 'metal', 'plastic', 'wood')."
    weight_prompt = "Estimate the weight of this object in grams or kilograms. If you can't be specific, use 'light' (<100g), 'medium' (100g-1kg), or 'heavy' (>1kg)."
    situation_prompt = "Describe what is happening with this object. Is it being picked up, held, placed, lifted? Answer in one short sentence."
    
    material = self._query_vlm(pil_image, material_prompt)
    weight = self._query_vlm(pil_image, weight_prompt)
    situation = self._query_vlm(pil_image, situation_prompt)
    
    return {
        "material": material.strip(),
        "weight": weight.strip(),
        "situation": situation.strip()
    }
```

### Example 2: Color Mask Overlay
```python
# In video_pipeline.py
def apply_color_mask(frame: np.ndarray, mask: np.ndarray, color: Tuple[int, int, int], alpha: float = 0.4) -> np.ndarray:
    """Apply semi-transparent color mask overlay."""
    overlay = frame.copy()
    mask_3d = np.stack([mask, mask, mask], axis=-1).astype(np.uint8)
    color_mask = np.zeros_like(frame)
    color_mask[mask] = color
    return cv2.addWeighted(overlay, 1 - alpha, color_mask, alpha, 0)
```

### Example 3: Multi-Object Detection
```python
# In multi_object_detector.py (new file)
def detect_hands_and_object(video_path: str, object_prompt: str, predictor) -> Dict:
    """Detect both hands and target object in video."""
    # Session 1: Detect hands
    response1 = predictor.handle_request(dict(type="start_session", resource_path=video_path))
    session_id_hands = response1["session_id"]
    predictor.handle_request(dict(type="add_prompt", session_id=session_id_hands, frame_index=0, text="hand"))
    hands_masks = {}
    for response in predictor.handle_stream_request(dict(type="propagate_in_video", session_id=session_id_hands)):
        hands_masks[response["frame_index"]] = extract_primary_mask(response["outputs"], response["frame_index"])
    
    # Session 2: Detect object
    response2 = predictor.handle_request(dict(type="start_session", resource_path=video_path))
    session_id_obj = response2["session_id"]
    predictor.handle_request(dict(type="add_prompt", session_id=session_id_obj, frame_index=0, text=object_prompt))
    object_masks = {}
    for response in predictor.handle_stream_request(dict(type="propagate_in_video", session_id=session_id_obj)):
        object_masks[response["frame_index"]] = extract_primary_mask(response["outputs"], response["frame_index"])
    
    return {"hands": hands_masks, "object": object_masks}
```

---

## Next Steps

1. **Start with Task 1:** Enhance VLM analysis (easiest, immediate impact)
2. **Then Task 3:** Color masks (visual improvement)
3. **Then Task 2:** Multi-object detection (enables hands + object)
4. **Finally Task 4:** Wireframe (polish)

---

## Notes

- **Performance:** Multi-object detection will double SAM 3 processing time (two sessions)
- **Memory:** Two SAM 3 sessions may use more GPU memory
- **Colors:** Adjust fluorescent colors based on visibility in MR headset videos
- **Wireframe:** Start simple (2D), add 3D later if time permits


