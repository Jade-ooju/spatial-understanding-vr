# SAM 3 Installation Script for Windows
# This script automates the installation of SAM 3 in a conda environment on D drive
# Requires: Miniconda/Anaconda, CUDA Toolkit 12.6+, Visual Studio Build Tools

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SAM 3 Installation Script (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 0: Check prerequisites
Write-Host "Step 0: Checking prerequisites..." -ForegroundColor Yellow

# Check if conda is available
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "Error: conda is not found in PATH" -ForegroundColor Red
    Write-Host "Please install Miniconda/Anaconda and add it to PATH" -ForegroundColor Red
    exit 1
}

# Check if CUDA is available (optional but recommended)
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    Write-Host "CUDA GPU detected:" -ForegroundColor Green
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
    Write-Host ""
} else {
    Write-Host "Warning: No NVIDIA GPU detected. SAM 3 will run on CPU (very slow)." -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

# Get project root directory (parent of scripts directory)
$ScriptDir = Split-Path -Parent $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir
$SAMDir = Join-Path $ProjectRoot "SAM"

# Step 1: Configure conda to use D drive for environments
Write-Host ""
Write-Host "Step 1: Configuring conda to use D drive for environments..." -ForegroundColor Yellow

# Check if conda envs directory is already on D drive
$CondaBase = conda info --base
$CondaEnvsPath = conda config --show envs_dirs | Select-String -Pattern "envs_dirs:" | ForEach-Object { $_.Line.Split(":")[1].Trim() }

# Set conda envs directory to D drive if not already set
$DDriveEnvsPath = "D:\conda\envs"
if (-not (Test-Path $DDriveEnvsPath)) {
    Write-Host "Creating D:\conda\envs directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $DDriveEnvsPath -Force | Out-Null
}

# Add D drive to conda envs directories if not already there
$envsDirs = conda config --show envs_dirs
if ($envsDirs -notlike "*$DDriveEnvsPath*") {
    Write-Host "Adding D drive to conda envs directories..." -ForegroundColor Yellow
    conda config --add envs_dirs $DDriveEnvsPath
}

Write-Host "Conda environments will be stored in: $DDriveEnvsPath" -ForegroundColor Green

# Step 2: Clone SAM 3 repository
Write-Host ""
Write-Host "Step 2: Cloning SAM 3 repository..." -ForegroundColor Yellow

if (Test-Path $SAMDir) {
    if (Test-Path (Join-Path $SAMDir ".git")) {
        Write-Host "SAM 3 repository already exists. Updating..." -ForegroundColor Yellow
        Push-Location $SAMDir
        git pull
        Pop-Location
    } else {
        Write-Host "SAM directory exists but is not a git repository. Removing..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $SAMDir
        git clone https://github.com/facebookresearch/sam3.git $SAMDir
    }
} else {
    Write-Host "Cloning SAM 3 from GitHub..." -ForegroundColor Yellow
    git clone https://github.com/facebookresearch/sam3.git $SAMDir
}

Write-Host "SAM 3 cloned to: $SAMDir" -ForegroundColor Green

# Step 3: Create conda environment on D drive
Write-Host ""
Write-Host "Step 3: Creating conda environment 'sam3' with Python 3.12 on D drive..." -ForegroundColor Yellow

$envExists = conda env list | Select-String -Pattern "^sam3\s"
if ($envExists) {
    Write-Host "Environment 'sam3' already exists." -ForegroundColor Yellow
    $response = Read-Host "Remove and recreate? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        conda env remove -n sam3 -y
        conda create -n sam3 python=3.12 -y
    } else {
        Write-Host "Using existing environment." -ForegroundColor Yellow
    }
} else {
    conda create -n sam3 python=3.12 -y
}

# Step 4: Activate environment and install PyTorch
Write-Host ""
Write-Host "Step 4: Installing PyTorch 2.7.0 with CUDA 12.6 support..." -ForegroundColor Yellow

# Get conda base path and activate script
$CondaBase = conda info --base
$ActivateScript = Join-Path $CondaBase "Scripts\activate.ps1"

# Activate environment using conda run (more reliable in scripts)
Write-Host "Activating sam3 environment..." -ForegroundColor Yellow

# Install PyTorch with CUDA using conda run
conda run -n sam3 pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Verify GPU
Write-Host ""
Write-Host "Verifying GPU setup..." -ForegroundColor Yellow
conda run -n sam3 python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

# Step 5: Install SAM 3
Write-Host ""
Write-Host "Step 5: Installing SAM 3 package from cloned repository..." -ForegroundColor Yellow

Push-Location $SAMDir
conda run -n sam3 pip install -e .

# Ask about optional dependencies
Write-Host ""
$response = Read-Host "Install dependencies for example notebooks? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Installing notebook dependencies..." -ForegroundColor Yellow
    conda run -n sam3 pip install -e ".[notebooks]"
}

Write-Host ""
$response = Read-Host "Install development and training dependencies? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "Installing dev and train dependencies..." -ForegroundColor Yellow
    conda run -n sam3 pip install -e ".[dev,train]"
}

Pop-Location

# Step 6: Install VLM and project dependencies
Write-Host ""
Write-Host "Step 6: Installing VLM and project dependencies..." -ForegroundColor Yellow

# Install VLM dependencies (Moondream2)
conda run -n sam3 pip install transformers pillow

# Install project dependencies
$ProjectDir = Split-Path -Parent $ScriptDir
conda run -n sam3 pip install opencv-python numpy tqdm

# Step 7: Verify installation
Write-Host ""
Write-Host "Step 7: Verifying installation..." -ForegroundColor Yellow

conda run -n sam3 python -c "from sam3.model_builder import build_sam3_video_predictor; print('✓ SAM 3 installed successfully!')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Installation verification failed!" -ForegroundColor Red
    exit 1
}

# Test VLM
Write-Host ""
Write-Host "Testing VLM (PhysicsEstimator)..." -ForegroundColor Yellow

# Create temporary Python script file
$TempScript = Join-Path $env:TEMP "test_vlm_$(Get-Random).py"
$VLMTestScript = @"
import sys
sys.path.insert(0, r'$ProjectDir\video_pipeline')
from physics_estimator import PhysicsEstimator
import numpy as np

# Test image
img = np.zeros((224, 224, 3), dtype=np.uint8)
y, x = np.ogrid[:224, :224]
mask = (x-112)**2 + (y-112)**2 <= 50**2
img[mask] = 255

# Test VLM
est = PhysicsEstimator()
print('VLM initialized:', est.initialized)
if est.initialized:
    result = est.analyze(img)
    print('Result:', result)
"@

# Write to temp file
$VLMTestScript | Out-File -FilePath $TempScript -Encoding utf8

# Execute the script
conda run -n sam3 python $TempScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: VLM test failed, but this is optional" -ForegroundColor Yellow
}

# Clean up temp file
Remove-Item -Path $TempScript -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use SAM 3:" -ForegroundColor Yellow
Write-Host "  1. Activate the environment: conda activate sam3" -ForegroundColor White
Write-Host "  2. Request access to SAM 3 checkpoints: https://huggingface.co/facebook/sam3" -ForegroundColor White
Write-Host "  3. Authenticate: hf auth login" -ForegroundColor White
Write-Host "  4. Run the pipeline from spatial-understanding-vr directory:" -ForegroundColor White
Write-Host "     conda activate sam3" -ForegroundColor White
Write-Host "     python video_pipeline/video_pipeline.py --video resources/video.mp4 --prompt `"spoon`"" -ForegroundColor White
Write-Host ""
Write-Host "Conda environment location: $DDriveEnvsPath\sam3" -ForegroundColor Cyan
Write-Host "SAM 3 repository location: $SAMDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy segmenting! 🎉" -ForegroundColor Green

