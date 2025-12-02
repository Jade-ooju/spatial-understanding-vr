# Push to GitHub - Step by Step Guide

## 🚀 Quick Push Instructions

### Step 1: Navigate to the folder
```bash
cd /home/jade/sam3/spatial-understanding-vr
```

### Step 2: Initialize Git repository
```bash
git init
```

### Step 3: Add all files
```bash
git add .
```

### Step 4: Create initial commit
```bash
git commit -m "Initial commit: Video pipeline for VR spatial understanding with SAM 3 and VLM"
```

### Step 5: Add remote repository
```bash
git remote add origin https://github.com/Jade-ooju/spatial-understanding-vr.git
```

### Step 6: Set main branch
```bash
git branch -M main
```

### Step 7: Push to GitHub
```bash
git push -u origin main
```

## 📋 Complete Command Sequence

Copy and paste this entire block:

```bash
cd /home/jade/sam3/spatial-understanding-vr
git init
git add .
git commit -m "Initial commit: Video pipeline for VR spatial understanding with SAM 3 and VLM"
git remote add origin https://github.com/Jade-ooju/spatial-understanding-vr.git
git branch -M main
git push -u origin main
```

## 🔐 Authentication

If you're prompted for authentication:

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with `repo` scope
3. Use the token as your password when prompted

### Option 2: SSH (If configured)
```bash
git remote set-url origin git@github.com:Jade-ooju/spatial-understanding-vr.git
git push -u origin main
```

## ✅ Verification

After pushing, verify on GitHub:
1. Go to https://github.com/Jade-ooju/spatial-understanding-vr
2. Check that all files are visible
3. Verify README.md displays correctly

## 📝 What Will Be Uploaded

- ✅ All scripts in `video_pipeline/`
- ✅ All documentation in `docs/`
- ✅ Test files in `tests/`
- ✅ Utility scripts in `scripts/`
- ✅ README and configuration files
- ✅ SAM3_LICENSE file

## ❌ What Will NOT Be Uploaded (via .gitignore)

- ❌ Large video files (`*.mp4`, `*.mkv`)
- ❌ Log files (`*.log`)
- ❌ Python cache (`__pycache__/`)
- ❌ Model checkpoints
- ❌ Output files

## 🔍 Troubleshooting

### "Repository not found"
- Check repository name: `Jade-ooju/spatial-understanding-vr`
- Verify you have push access
- Check if repository exists on GitHub

### "Authentication failed"
- Use Personal Access Token instead of password
- Or set up SSH keys

### "Large file" error
- Check `.gitignore` is working
- Use Git LFS for large files if needed

### "Nothing to commit"
- Check `git status` to see what's staged
- Verify files are in the directory

## 🎯 After Successful Push

Your repository will be available at:
**https://github.com/Jade-ooju/spatial-understanding-vr**

Users can then:
1. Clone the repository
2. Install SAM 3: `pip install git+https://github.com/facebookresearch/sam3.git`
3. Install dependencies: `pip install opencv-python transformers torch numpy`
4. Run the pipeline!

