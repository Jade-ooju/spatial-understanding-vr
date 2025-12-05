# Windows Setup Guide for Spatial Understanding VR Pipeline

This guide provides step-by-step instructions for setting up the SAM 3 + VLM video pipeline on Windows with GPU support.

## Prerequisites

Before starting, ensure you have:

1. **Miniconda or Anaconda** installed for Windows
   - Download from: https://docs.conda.io/en/latest/miniconda.html
   - Add conda to PATH during installation

2. **CUDA Toolkit 12.6+** (for GPU acceleration)
   - Download from: https://developer.nvidia.com/cuda-downloads
   - Verify installation: `nvidia-smi` should show your GPU

3. **Visual Studio Build Tools** (C++ workload)
   - Required for compiling some Python packages
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Install "Desktop development with C++" workload

4. **Git** for Windows
   - Download from: https://git-scm.com/download/win

## Quick Setup (Automated)

### Option 1: Run the PowerShell Script

1. Open PowerShell as Administrator (recommended) or regular user
2. Navigate to the project directory:
   ```powershell
   cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr
   ```
3. Run the setup script:
   ```powershell
   .\scripts\install_sam3_windows.ps1
   ```

The script will:
- Configure conda to use D drive for environments
- Clone SAM 3 into the `SAM` folder (if not already done)
- Create conda environment `sam3` on D drive
- Install PyTorch with CUDA 12.6 support
- Install SAM 3 from the cloned repository
- Install VLM and project dependencies
- Verify the installation

### Option 2: Manual Setup

If you prefer manual setup or the script fails, follow these steps:

#### Step 1: Configure Conda for D Drive

```powershell
# Create directory for conda environments on D drive
New-Item -ItemType Directory -Path "D:\conda\envs" -Force

# Add D drive to conda envs directories
conda config --add envs_dirs D:\conda\envs

# Verify
conda config --show envs_dirs
```

#### Step 2: Clone SAM 3 (if not already done)

The SAM 3 repository should already be cloned in `D:\OOJU\Projects\SpatialUnderstanding\SAM`. If not:

```powershell
cd D:\OOJU\Projects\SpatialUnderstanding
git clone https://github.com/facebookresearch/sam3.git SAM
```

#### Step 3: Create Conda Environment

```powershell
# Create environment with Python 3.12
conda create -n sam3 python=3.12 -y

# Activate environment
conda activate sam3
```

#### Step 4: Install PyTorch with CUDA

```powershell
# Install PyTorch 2.7.0 with CUDA 12.6
pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Verify GPU
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

**Expected output:** `CUDA: True` and your GPU name

#### Step 5: Install SAM 3

```powershell
# Navigate to SAM directory
cd D:\OOJU\Projects\SpatialUnderstanding\SAM

# Install SAM 3 in editable mode
pip install -e .

# Install notebook dependencies (optional)
pip install -e ".[notebooks]"
```

#### Step 6: Install VLM and Project Dependencies

```powershell
# Install VLM dependencies (Moondream2)
pip install transformers pillow

# Navigate to project directory
cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr

# Install project dependencies
pip install opencv-python numpy tqdm
```

#### Step 7: Authenticate Hugging Face

SAM 3 requires Hugging Face authentication for model checkpoints:

```powershell
# Install huggingface_hub if not already installed
pip install huggingface_hub

# Authenticate
hf auth login
```

Follow the prompts to authenticate. You'll need to:
1. Request access at: https://huggingface.co/facebook/sam3
2. Get your token from: https://huggingface.co/settings/tokens

## Verification

### Test GPU Setup

```powershell
conda activate sam3
python -c "import torch; x = torch.randn(1000, 1000).cuda(); y = torch.randn(1000, 1000).cuda(); z = x @ y; print('GPU test OK:', z.shape)"
```

**Expected:** `GPU test OK: torch.Size([1000, 1000])`

### Test SAM 3

```powershell
conda activate sam3
python -c "from sam3.model_builder import build_sam3_video_predictor; print('✓ SAM 3 installed successfully!')"
```

**Expected:** `✓ SAM 3 installed successfully!`

### Test VLM

```powershell
conda activate sam3
cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr
python -c "import sys; sys.path.insert(0, 'video_pipeline'); from physics_estimator import PhysicsEstimator; import numpy as np; img = np.zeros((224, 224, 3), dtype=np.uint8); y, x = np.ogrid[:224, :224]; mask = (x-112)**2 + (y-112)**2 <= 50**2; img[mask] = 255; est = PhysicsEstimator(); print('VLM initialized:', est.initialized)"
```

**Expected:** `VLM initialized: True`

## Running the Pipeline

Once setup is complete:

```powershell
# Activate environment
conda activate sam3

# Navigate to project directory
cd D:\OOJU\Projects\SpatialUnderstanding\spatial-understanding-vr

# Run pipeline
python video_pipeline/video_pipeline.py `
  --video resources/video.mp4 `
  --prompt "spoon" `
  --vlm-interval 30 `
  --output outputs/result.mp4
```

## Troubleshooting

### CUDA Not Working

1. **Check GPU detection:**
   ```powershell
   nvidia-smi
   ```
   Should show your GPU. If not, reinstall NVIDIA drivers.

2. **Reinstall PyTorch with CUDA:**
   ```powershell
   pip uninstall torch torchvision torchaudio -y
   pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
   ```

3. **Verify CUDA version:**
   ```powershell
   python -c "import torch; print(torch.version.cuda)"
   ```
   Should match your CUDA Toolkit version.

### VLM Not Working

1. **Install dependencies:**
   ```powershell
   pip install transformers torch pillow
   ```

2. **Authenticate Hugging Face:**
   ```powershell
   hf auth login
   ```

3. **Check internet connection** (models download from Hugging Face)

### Import Errors

1. **Activate environment:**
   ```powershell
   conda activate sam3
   ```

2. **Reinstall SAM 3:**
   ```powershell
   cd D:\OOJU\Projects\SpatialUnderstanding\SAM
   pip install -e .
   ```

3. **Check Python path:**
   ```powershell
   python -c "import sys; print(sys.path)"
   ```

### Conda Environment Not on D Drive

If the environment was created on C drive instead:

1. **Remove existing environment:**
   ```powershell
   conda env remove -n sam3 -y
   ```

2. **Verify D drive is in envs_dirs:**
   ```powershell
   conda config --show envs_dirs
   ```

3. **Recreate environment:**
   ```powershell
   conda create -n sam3 python=3.12 -y
   ```

4. **Verify location:**
   ```powershell
   conda env list
   ```
   Should show `D:\conda\envs\sam3`

## Performance Expectations

- **With GPU**: 5-10 fps, ~2-4 min for 121 frames
- **Without GPU**: 0.02 fps, ~85 min for 121 frames
- **Memory**: 6-8GB GPU VRAM recommended

## Directory Structure

After setup, your directories should look like:

```
D:\OOJU\Projects\SpatialUnderstanding\
├── SAM\                          # SAM 3 repository (cloned)
│   ├── sam3\                     # SAM 3 package
│   └── ...
└── spatial-understanding-vr\     # Project directory
    ├── video_pipeline\
    ├── scripts\
    │   └── install_sam3_windows.ps1
    └── ...

D:\conda\envs\
└── sam3\                         # Conda environment on D drive
    ├── python.exe
    └── ...
```

## Next Steps

1. **Request SAM 3 checkpoint access**: https://huggingface.co/facebook/sam3
2. **Authenticate**: `hf auth login`
3. **Test with a sample video**: See `docs/VIDEO_PIPELINE_USAGE.md`
4. **Read documentation**: See `docs/README.md` for full documentation

## Support

For issues or questions:
- Check `docs/` directory for detailed documentation
- Review error messages carefully
- Ensure all prerequisites are installed
- Verify GPU drivers are up to date

