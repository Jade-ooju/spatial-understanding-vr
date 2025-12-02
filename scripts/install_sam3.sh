#!/bin/bash
# SAM 3 Installation Script for Ubuntu 22.04
# This script automates the installation of SAM 3 in a conda environment

set -e  # Exit on error

echo "=========================================="
echo "SAM 3 Installation Script"
echo "=========================================="
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not found in PATH"
    echo "Please initialize conda first:"
    echo "  source ~/miniconda3/etc/profile.d/conda.sh"
    exit 1
fi

# Check if CUDA is available (optional but recommended)
if command -v nvidia-smi &> /dev/null; then
    echo "CUDA GPU detected:"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
    echo ""
else
    echo "Warning: No NVIDIA GPU detected. SAM 3 will run on CPU (very slow)."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Create conda environment
echo "Step 1: Creating conda environment 'sam3' with Python 3.12..."
if conda env list | grep -q "^sam3 "; then
    echo "Environment 'sam3' already exists."
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        conda env remove -n sam3 -y
        conda create -n sam3 python=3.12 -y
    else
        echo "Using existing environment."
    fi
else
    conda create -n sam3 python=3.12 -y
fi

# Step 2: Activate environment
echo ""
echo "Step 2: Activating conda environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate sam3

# Step 3: Install PyTorch
echo ""
echo "Step 3: Installing PyTorch 2.7.0 with CUDA 12.6 support..."
pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Step 4: Navigate to sam3 directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 5: Install SAM 3
echo ""
echo "Step 4: Installing SAM 3 package..."
pip install -e .

# Step 6: Ask about optional dependencies
echo ""
read -p "Install dependencies for example notebooks? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing notebook dependencies..."
    pip install -e ".[notebooks]"
fi

echo ""
read -p "Install development and training dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing dev and train dependencies..."
    pip install -e ".[dev,train]"
fi

# Step 7: Verify installation
echo ""
echo "Step 5: Verifying installation..."
python -c "from sam3.model_builder import build_sam3_image_model; print('✓ SAM 3 installed successfully!')" || {
    echo "✗ Installation verification failed!"
    exit 1
}

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To use SAM 3:"
echo "  1. Activate the environment: conda activate sam3"
echo "  2. Request access to SAM 3 checkpoints: https://huggingface.co/facebook/sam3"
echo "  3. Authenticate: hf auth login"
echo "  4. Check out the examples in the examples/ directory"
echo ""
echo "Happy segmenting! 🎉"

