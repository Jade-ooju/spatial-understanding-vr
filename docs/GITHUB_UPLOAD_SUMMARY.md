# GitHub Upload - Legal Summary

## ✅ You CAN Upload Your Code!

**Short Answer**: Yes, you can upload your video pipeline code to GitHub. The SAM 3 license allows creating and distributing derivative works.

## 📋 What the SAM 3 License Allows

According to the [SAM 3 License](https://github.com/facebookresearch/sam3/blob/main/LICENSE):

✅ **You CAN**:
- Create derivative works (your pipeline code)
- Distribute your derivative works
- Modify and use SAM 3
- Own your derivative works (Section 5a)

⚠️ **You MUST**:
- Include the SAM 3 LICENSE file when distributing
- Acknowledge use of SAM 3 in publications
- Comply with applicable laws
- Not use for prohibited purposes (military, weapons, etc.)

## 🎯 What to Upload

### ✅ Include in Your Repo:
1. **Your code only**:
   - `scripts/video_pipeline/video_pipeline.py`
   - `scripts/video_pipeline/physics_estimator.py`
   - `scripts/video_pipeline/monitor_progress.sh`
   - All documentation

2. **SAM 3 LICENSE file**:
   - Copy from SAM 3 repo
   - Name it `SAM3_LICENSE` or place in `docs/`

3. **Proper attribution**:
   - Credit SAM 3 in README
   - Add license headers to your code

### ❌ DON'T Include:
1. **SAM 3 source code** (`sam3/` directory)
2. **Model checkpoints** (`.pth`, `.pt` files)
3. **Large video files** (use Git LFS or external storage)

## 🚀 Quick Setup Steps

1. **Create `.gitignore`** (see `.gitignore.template`)
2. **Copy SAM 3 LICENSE** as `SAM3_LICENSE`
3. **Update README** with attribution (see `REPO_README_TEMPLATE.md`)
4. **Add license headers** to your Python files
5. **Create your own LICENSE** (MIT, Apache, etc.)

## 📝 Key Legal Points

1. **You own your code**: Section 5a states you own derivative works you create
2. **Must include SAM 3 LICENSE**: Required when redistributing (Section 1.b.i)
3. **Must acknowledge**: Required in publications (Section 1.b.ii)
4. **Prohibited uses**: No military, weapons, etc. (Section 1.b.v)

## 🔗 References

- [SAM 3 License](https://github.com/facebookresearch/sam3/blob/main/LICENSE)
- [SAM 3 Repository](https://github.com/facebookresearch/sam3)
- [Full Upload Guide](docs/video_pipeline/GITHUB_UPLOAD_GUIDE.md)

## 💡 Best Practice

**Make SAM 3 a dependency, not part of your repo**:
- Users install SAM 3 via `pip install git+https://github.com/facebookresearch/sam3.git`
- Your code imports and uses SAM 3
- Include SAM 3 LICENSE for compliance
- This is the cleanest and most legal approach

## ⚠️ Important

This is not legal advice. For commercial use or if you have concerns, consult a lawyer familiar with software licensing.

