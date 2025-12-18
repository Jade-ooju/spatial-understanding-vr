# Quick Start Guide - Windows

This is a condensed guide for Windows users. For detailed instructions, see `SETUP_WINDOWS.md`.

## Prerequisites Checklist

- [ ] Miniconda/Anaconda installed
- [ ] CUDA Toolkit 12.6+ installed
- [ ] Visual Studio Build Tools (C++ workload) installed
- [ ] Git for Windows installed
- [ ] GPU drivers up to date (`nvidia-smi` works)

## Quick Setup (5 minutes)

### 1. Run the Setup Script

Open PowerShell in the project directory:

```powershell
cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr
.\scripts\install_sam3_windows.ps1
```

The script will:
- ✅ Configure conda to use D drive for environments
- ✅ Clone SAM 3 (if needed)
- ✅ Create `sam3` conda environment on D drive
- ✅ Install PyTorch with CUDA
- ✅ Install SAM 3 and dependencies
- ✅ Verify installation

### 2. Authenticate Hugging Face

```powershell
conda activate sam3
hf auth login
```

**Note:** You need to:
1. Request access at: https://huggingface.co/facebook/sam3
2. Get your token from: https://huggingface.co/settings/tokens

### 3. Verify Setup

```powershell
conda activate sam3
.\scripts\verify_setup.ps1
```

All checks should pass ✓

## Running the Pipeline

```powershell
# Activate environment
conda activate sam3

# Navigate to project
cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr

# Run pipeline
python video_pipeline/video_pipeline.py `
  --video resources/video.mp4 `
  --prompt "spoon" `
  --vlm-interval 30 `
  --output outputs/result.mp4
```

## Quick Troubleshooting

**CUDA not working?**
```powershell
nvidia-smi  # Should show GPU
python -c "import torch; print(torch.cuda.is_available())"  # Should be True
```

**SAM 3 import error?**
```powershell
conda activate sam3
cd D:\OOJU\Projects\SpatialUnderstanding\SAM
pip install -e .
```

**VLM not working?**
```powershell
conda activate sam3
pip install transformers pillow
hf auth login
```

## Directory Structure

```
D:\OOJU\Projects\SpatialUnderstanding\
├── SAM\                    # SAM 3 repository (cloned)
└── spatial-understanding-vr\
    ├── video_pipeline\
    ├── scripts\
    │   ├── install_sam3_windows.ps1
    │   └── verify_setup.ps1
    └── ...

D:\conda\envs\
└── sam3\                   # Conda environment on D drive
```

## Performance

- **With GPU**: 5-10 fps, ~2-4 min for 121 frames
- **Without GPU**: 0.02 fps, ~85 min for 121 frames ⚠️

## Next Steps

1. Read `SETUP_WINDOWS.md` for detailed instructions
2. Read `docs/VIDEO_PIPELINE_USAGE.md` for pipeline usage
3. Test with a sample video

## Support

- Detailed setup: `SETUP_WINDOWS.md`
- Pipeline usage: `docs/VIDEO_PIPELINE_USAGE.md`
- Full documentation: `docs/README.md`






