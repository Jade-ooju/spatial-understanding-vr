# GitHub Upload Guide - Legal Considerations

## ✅ Good News: You Can Upload Your Code!

Based on the [SAM 3 License](https://github.com/facebookresearch/spatial-understanding-vr/blob/main/LICENSE), you **can** upload your video pipeline code to GitHub. Here's what you need to know:

## 📋 SAM 3 License Summary

The SAM 3 license allows:
- ✅ Creating derivative works (your pipeline code)
- ✅ Distributing derivative works
- ✅ Modifying and using SAM 3

**Requirements**:
- Include the SAM 3 LICENSE file
- Acknowledge use of SAM 3
- Comply with applicable laws
- Cannot use for prohibited purposes (military, weapons, etc.)

## 🎯 Recommended Approach

### ✅ DO Include:
1. **Your own code**:
   - `video_pipeline/video_pipeline.py`
   - `video_pipeline/physics_estimator.py`
   - `video_pipeline/monitor_progress.sh`
   - All documentation in `docs/`

2. **SAM 3 LICENSE file**:
   - Copy `LICENSE` from SAM 3 repository
   - Place it in your repo root as `SAM3_LICENSE` or in `docs/`

3. **Proper attribution**:
   - Add attribution in your README
   - Reference SAM 3 in your code comments

### ❌ DON'T Include:
1. **SAM 3 source code**:
   - Don't copy the `spatial-understanding-vr/` directory
   - Don't include SAM 3 model files
   - Don't include SAM 3 checkpoints

2. **Large files**:
   - Don't commit model weights
   - Don't commit large video files (use Git LFS or external storage)

## 📝 Implementation Steps

### 1. Create `.gitignore`

```gitignore
# SAM 3 (install via pip, don't commit)
spatial-understanding-vr/
sam3.egg-info/

# Model checkpoints
*.pth
*.pt
*.ckpt
*.safetensors

# Large video files
*.mp4
*.mkv
*.avi
resources/*.mp4
resources/*.mkv

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### 2. Update Your README.md

Add a section like this:

```markdown
## Dependencies

This project uses [SAM 3](https://github.com/facebookresearch/sam3) for object segmentation.

### Installation

1. Install SAM 3:
   ```bash
   pip install git+https://github.com/facebookresearch/sam3.git
   ```

2. Install other dependencies:
   ```bash
   pip install opencv-python transformers torch
   ```

### Attribution

This project uses SAM 3 (Segment Anything Model 3) by Meta AI Research.
See [SAM3_LICENSE](SAM3_LICENSE) for license terms.
```

### 3. Add SAM 3 License File

```bash
# Copy SAM 3 license to your repo
cp /path/to/spatial-understanding-vr/LICENSE SAM3_LICENSE
```

### 4. Add License Header to Your Scripts

Add to the top of your Python files:

```python
#!/usr/bin/env python3
"""
Video Pipeline for VR Headset Videos

This script integrates SAM 3 (Segment Anything Model 3) and VLM for 
object segmentation and physical property analysis.

SAM 3 is used under the SAM License. See SAM3_LICENSE for details.
Copyright (c) Meta Platforms, Inc. and affiliates. All Rights Reserved.

This derivative work is licensed under [YOUR LICENSE].
"""
```

### 5. Create Your Own LICENSE

Choose an appropriate license for your code:
- **MIT License**: Permissive, allows commercial use
- **Apache 2.0**: Similar to MIT, includes patent grant
- **GPL v3**: Copyleft, requires derivative works to be open source

## 📦 Recommended Repository Structure

```
spatial-understanding-vr/
├── README.md                    # Your project README
├── LICENSE                      # Your license
├── SAM3_LICENSE                 # SAM 3 license (required)
├── .gitignore                   # Exclude SAM 3 code
├── requirements.txt             # Dependencies
├── scripts/
│   └── video_pipeline/          # Your code only
│       ├── video_pipeline.py
│       ├── physics_estimator.py
│       └── monitor_progress.sh
├── docs/
│   └── video_pipeline/          # Your documentation
└── resources/                   # Example videos (not committed)
    └── README.md                # Instructions to add videos
```

## ✅ Checklist Before Uploading

- [ ] Remove `spatial-understanding-vr/` directory (if copied)
- [ ] Remove model checkpoints
- [ ] Remove large video files
- [ ] Add `.gitignore`
- [ ] Copy SAM 3 LICENSE as `SAM3_LICENSE`
- [ ] Add attribution in README
- [ ] Add license headers to your code
- [ ] Create your own LICENSE file
- [ ] Update documentation with installation instructions
- [ ] Test that installation works without SAM 3 code

## 🔗 Legal References

- [SAM 3 License](https://github.com/facebookresearch/spatial-understanding-vr/blob/main/LICENSE)
- [SAM 3 Repository](https://github.com/facebookresearch/sam3)
- [SAM 3 Project Page](https://ai.meta.com/spatial-understanding-vr/)

## 💡 Best Practices

1. **Reference, Don't Copy**: Make SAM 3 a dependency, not part of your repo
2. **Clear Attribution**: Always credit SAM 3 in your documentation
3. **License Compliance**: Include the SAM 3 LICENSE file
4. **Documentation**: Clearly explain how to install SAM 3
5. **Your License**: Choose an appropriate license for your code

## 🚀 Quick Start for Your Repo

```bash
# 1. Initialize repo
cd /path/to/spatial-understanding-vr
git init

# 2. All code is already in this folder
# (video_pipeline/ and docs/ are already here)

# 3. SAM 3 license is already included as SAM3_LICENSE

# 4. Create .gitignore (see above)
# 5. Create README.md with attribution
# 6. Create LICENSE for your code
# 7. Commit and push
```

## ⚠️ Important Notes

1. **You own your derivative work**: The license states you own modifications you make
2. **Must include SAM 3 LICENSE**: Required when redistributing
3. **Cannot use for prohibited purposes**: Military, weapons, etc.
4. **Must acknowledge in publications**: If you publish research using this

## 📞 If You Have Questions

- Review the [SAM 3 License](https://github.com/facebookresearch/spatial-understanding-vr/blob/main/LICENSE) carefully
- Check [SAM 3 GitHub Issues](https://github.com/facebookresearch/spatial-understanding-vr/issues) for similar questions
- Consider consulting a lawyer for commercial use cases

