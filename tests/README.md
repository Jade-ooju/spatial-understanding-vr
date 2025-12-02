# Tests

This directory contains test scripts for SAM 3.

## Test Scripts

- `test_sam3.py` - Basic installation and functionality test
- `test_my_vr_image.py` - Test script for VR egocentric images with text prompts

## Usage

Run tests from the project root directory:

```bash
# Basic test
python tests/test_sam3.py

# Test with CPU mode
CUDA_VISIBLE_DEVICES="" python tests/test_sam3.py --force-cpu

# Test with custom image
python tests/test_my_vr_image.py <image_path> [text_prompt]
```

## Output

Test outputs (masks, visualizations) are saved to the `outputs/` directory in the project root.

