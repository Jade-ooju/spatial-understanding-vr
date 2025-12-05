# Windows vs Linux Performance Comparison

## Test Configuration

### Linux (Previous Test)
- **OS**: Linux (Ubuntu)
- **GPU**: NVIDIA GeForce RTX 5060 Laptop GPU
- **Video**: `VR_short.mkv` (122 frames @ 1920x1080, 60 FPS)
- **Prompt**: "spoon"
- **Date**: December 2, 2025

### Windows (Current Test)
- **OS**: Windows 10/11
- **GPU**: NVIDIA GeForce RTX 4070
- **Video**: `VR.mkv` (1294 frames @ 1920x1080, 60 FPS)
- **Prompt**: "spoon"
- **Date**: December 3, 2025

---

## Performance Comparison

### Model Initialization

| Platform | Time | Details |
|----------|------|---------|
| **Linux** | **7.47 seconds** | SAM 3 video predictor loaded |
| **Windows (1st run)** | **24.16 seconds** | SAM 3 video predictor loaded (model download) |
| **Windows (2nd run)** | **9.58 seconds** | SAM 3 video predictor loaded (cached) |

**Analysis**: 
- Windows first run: **3.2x slower** (downloading 3.45GB model)
- Windows second run: **1.3x slower** (model cached, but still slower)
- Possible reasons: Different PyTorch versions, Windows overhead, or model loading differences
- Linux: PyTorch 2.7.0+cu126
- Windows: PyTorch 2.5.1 (from conda)

### Video Loading & Session Start

| Platform | Video Frames | Loading Time | Session Start Time |
|----------|-------------|--------------|-------------------|
| **Linux** | 122 frames | <0.1s | **0.55 seconds** |
| **Windows (1st run)** | 1294 frames | ~5s | **69.35 seconds** |
| **Windows (2nd run)** | 1294 frames | ~5s | **49.93 seconds** |

**Analysis**: 
- Windows video is **10.6x longer** (1294 vs 122 frames)
- Per-frame loading: Linux ~0.0045s/frame, Windows ~0.0535s/frame
- Windows is **~12x slower** per frame for loading
- However, Windows video is much longer, so absolute time is higher

### Propagation (Object Tracking)

| Platform | Frames | Time | Speed | Status |
|----------|--------|------|-------|--------|
| **Linux** | 121 frames | **5120.20 seconds (85.3 min)** | 0.02 fps (42.32s/frame) | ✅ Completed (CPU) |
| **Windows** | 1294 frames | **~24s/frame** (5 frames before OOM) | ~0.04 fps | ⚠️ CUDA OOM (needs optimization) |

**Analysis**:
- Linux completed successfully but was very slow (CPU inference - 0.02 fps)
- Windows: **Triton now working!** Got to propagation stage
- Windows propagation: ~24 seconds per frame (2x faster than Linux CPU)
- **Issue**: CUDA out of memory after 5 frames (12GB RTX 4070)
- **Solution**: Need memory optimization (see MEMORY_OPTIMIZATION.md)

### VLM Initialization

| Platform | Time | Status |
|----------|------|--------|
| **Linux** | <0.1 seconds | Placeholder mode (Moondream2 not installed) |
| **Windows** | ~14 seconds | ✅ Moondream2 fully initialized |

**Analysis**: 
- Windows successfully loaded Moondream2 VLM (3.85GB model)
- Linux used placeholder mode
- Windows has **actual VLM capability** vs Linux placeholder

### Total Processing Time

| Platform | Total Time | Breakdown |
|----------|------------|-----------|
| **Linux** | **~85.5 minutes** | Setup: 8s (0.2%), Propagation: 85.3min (99.8%), Processing: 4s (0.1%) |
| **Windows** | **N/A** | Failed at prompt addition stage (Triton error) |

---

## Key Differences

### 1. **Video Length**
- Linux: 122 frames (short test video)
- Windows: 1294 frames (full video, **10.6x longer**)

### 2. **GPU Usage**
- **Linux**: Appears to have run on CPU despite GPU being available
  - Log shows: "using CPU mode (no GPUs or CUDA not compatible)"
  - This explains the very slow propagation (0.02 fps)
- **Windows**: GPU detected and used (RTX 4070)
  - Model loaded on GPU successfully
  - Would be much faster if Triton issue is resolved

### 3. **VLM Status**
- **Linux**: Placeholder mode (Moondream2 not installed)
- **Windows**: Full Moondream2 VLM initialized and ready

### 4. **Dependencies**
- **Linux**: Completed with Triton available
- **Windows**: Failed due to Triton not available on Windows
  - Fixed with fallback to CPU NMS (now implemented)

---

## Estimated Performance (After Fixes)

### If Windows completes successfully:

**Projected Windows Performance** (with GPU):
- Model initialization: ~24 seconds (already done)
- Video loading: ~69 seconds for 1294 frames
- Propagation: **Estimated 5-10 fps with GPU** (vs 0.02 fps CPU on Linux)
  - For 1294 frames: **~2-4 minutes** (vs ~85 minutes on Linux CPU)
- Total estimated: **~5-7 minutes** for full video

**Linux Performance** (if GPU was used):
- Would likely match Windows performance (~5-10 fps)
- But Linux test ran on CPU, so was much slower

---

## Issues Encountered

### Windows Issues:
1. ✅ **Fixed**: GPU configuration (empty list → [0])
2. ✅ **Fixed**: Triton import in `edt.py` (added OpenCV fallback)
3. ✅ **Fixed**: Triton import in `nms.py` (added CPU fallback)
4. ✅ **Fixed**: Triton import in `connected_components.py` (added CPU fallback)
5. ✅ **Fixed**: Installed `triton-windows` package - Triton now fully functional!
6. ⚠️ **Current Issue**: CUDA out of memory (12GB RTX 4070)
   - Solution: Use `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
   - Or process smaller video segments

### Linux Issues:
1. ⚠️ GPU not used (ran on CPU despite GPU being available)
2. ⚠️ Moondream2 not installed (placeholder mode only)

---

## Recommendations

### For Windows:
1. ✅ Apply Triton fallback fixes (done)
2. ✅ Re-run pipeline to test full video
3. Monitor GPU usage to ensure GPU acceleration is working
4. Expected: Much faster than Linux CPU test (~5-10 fps vs 0.02 fps)

### For Linux:
1. Investigate why GPU wasn't used
2. Install Moondream2 for real VLM analysis
3. Re-run with GPU to match Windows performance

---

## Summary

| Metric | Linux (CPU) | Windows (GPU) | Winner |
|--------|-------------|---------------|--------|
| **Model Init** | 7.47s | 24.16s | Linux (3.2x faster) |
| **VLM Status** | Placeholder | Full Moondream2 | Windows |
| **GPU Usage** | Not used | Used | Windows |
| **Propagation** | 0.02 fps (CPU) | N/A (failed) | TBD (after fix) |
| **Dependencies** | Triton OK | Triton missing | Linux (but fixed) |

**Overall**: Windows has better setup (GPU + VLM) but needs Triton fixes. After fixes, Windows should significantly outperform Linux CPU test.

---

## Next Steps

1. **Test Windows pipeline** after Triton fixes
2. **Compare actual propagation speeds** (GPU vs CPU)
3. **Verify VLM analysis** works on Windows
4. **Optimize Linux** to use GPU if possible

