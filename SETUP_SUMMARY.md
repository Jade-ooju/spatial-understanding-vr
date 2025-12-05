# Setup Summary - Windows Configuration

## What Has Been Done

### ✅ Completed Tasks

1. **SAM 3 Repository Cloned**
   - Location: `D:\OOJU\Projects\SpatialUnderstanding\SAM`
   - Source: https://github.com/facebookresearch/sam3.git
   - Status: Ready for installation

2. **Windows Setup Scripts Created**
   - `scripts/install_sam3_windows.ps1` - Automated installation script
   - `scripts/verify_setup.ps1` - Verification script
   - Both scripts configured for D drive conda environments

3. **Documentation Created**
   - `SETUP_WINDOWS.md` - Comprehensive setup guide
   - `QUICK_START_WINDOWS.md` - Quick reference guide
   - `SETUP_SUMMARY.md` - This summary document

## What You Need To Do

### Step 1: Run the Setup Script

Open PowerShell and run:

```powershell
cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr
.\scripts\install_sam3_windows.ps1
```

**What the script does:**
- Configures conda to use `D:\conda\envs` for environments
- Creates `sam3` conda environment on D drive
- Installs PyTorch 2.7.0 with CUDA 12.6 support
- Installs SAM 3 from the cloned repository in `SAM` folder
- Installs VLM dependencies (Moondream2)
- Installs project dependencies (OpenCV, NumPy, etc.)
- Verifies the installation

**Expected time:** 10-20 minutes (depending on internet speed)

### Step 2: Authenticate Hugging Face

After the script completes:

```powershell
conda activate sam3
hf auth login
```

**Requirements:**
1. Request access to SAM 3 checkpoints: https://huggingface.co/facebook/sam3
2. Get your Hugging Face token: https://huggingface.co/settings/tokens
3. Run `hf auth login` and paste your token

### Step 3: Verify Installation

```powershell
conda activate sam3
.\scripts\verify_setup.ps1
```

All checks should pass ✓

## Key Features

### D Drive Configuration
- Conda environments will be stored in `D:\conda\envs\sam3`
- This matches your requirement to save conda environments on D drive

### SAM 3 Local Installation
- SAM 3 is cloned in `D:\OOJU\Projects\SpatialUnderstanding\SAM`
- Installation uses `pip install -e .` from the local repository
- This allows you to use SAM 3 resources directly

### GPU Support
- Script installs PyTorch with CUDA 12.6 support
- Automatically detects GPU and verifies CUDA availability
- Falls back to CPU if GPU not available (with warning)

## Directory Structure After Setup

```
D:\OOJU\Projects\SpatialUnderstanding\
├── SAM\                                    # SAM 3 repository (cloned)
│   ├── sam3\                               # SAM 3 package
│   ├── examples\                           # Example notebooks
│   └── ...
└── spatial-understanding-vr\               # Your project
    ├── video_pipeline\
    │   ├── video_pipeline.py
    │   └── physics_estimator.py
    ├── scripts\
    │   ├── install_sam3_windows.ps1       # Setup script
    │   └── verify_setup.ps1                # Verification script
    ├── SETUP_WINDOWS.md                    # Detailed guide
    ├── QUICK_START_WINDOWS.md              # Quick reference
    └── ...

D:\conda\envs\
└── sam3\                                   # Conda environment (created by script)
    ├── python.exe
    ├── Scripts\
    └── ...
```

## Troubleshooting

If the setup script fails:

1. **Check prerequisites:**
   - Miniconda/Anaconda installed
   - CUDA Toolkit 12.6+ installed
   - Visual Studio Build Tools installed
   - Git for Windows installed

2. **Manual installation:**
   - Follow the manual steps in `SETUP_WINDOWS.md`

3. **Common issues:**
   - See "Troubleshooting" section in `SETUP_WINDOWS.md`

## Next Steps After Setup

1. **Test the pipeline:**
   ```powershell
   conda activate sam3
   python video_pipeline/video_pipeline.py --video resources/video.mp4 --prompt "spoon"
   ```

2. **Read documentation:**
   - `docs/VIDEO_PIPELINE_USAGE.md` - How to use the pipeline
   - `docs/README.md` - Full documentation index

3. **Explore examples:**
   - Check `SAM/examples/` for SAM 3 example notebooks

## Script Details

### install_sam3_windows.ps1

**Features:**
- Automated conda environment setup on D drive
- GPU detection and CUDA verification
- SAM 3 installation from local repository
- VLM and project dependencies installation
- Comprehensive error handling

**Usage:**
```powershell
.\scripts\install_sam3_windows.ps1
```

### verify_setup.ps1

**Features:**
- Checks conda environment activation
- Verifies GPU/CUDA availability
- Tests SAM 3 import
- Tests VLM initialization
- Checks project dependencies
- Verifies directory structure

**Usage:**
```powershell
conda activate sam3
.\scripts\verify_setup.ps1
```

## Notes

- The setup script uses `conda run -n sam3` to execute commands in the environment, which is more reliable in PowerShell scripts
- All paths are calculated relative to the script location
- The script handles existing environments and repositories gracefully
- SAM 3 is installed in editable mode (`-e`) so changes to the repository are immediately available

## Support

For detailed instructions, see:
- `SETUP_WINDOWS.md` - Complete setup guide
- `QUICK_START_WINDOWS.md` - Quick reference
- `docs/VIDEO_PIPELINE_USAGE.md` - Pipeline usage guide



