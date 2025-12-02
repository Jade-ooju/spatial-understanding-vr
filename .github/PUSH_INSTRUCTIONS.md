# Push Instructions - Quick Reference

## 🚀 Push to GitHub (3 Commands)

```bash
cd /home/jade/sam3/spatial-understanding-vr

# 1. Commit all files
git add .
git commit -m "Initial commit: Video pipeline for VR spatial understanding"

# 2. Connect to GitHub
git remote add origin https://github.com/Jade-ooju/spatial-understanding-vr.git
git branch -M main

# 3. Push
git push -u origin main
```

## 🔐 If Authentication Required

Use a **Personal Access Token** (not password):
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate token with `repo` scope
3. Use token as password when prompted

## ✅ Verify

After pushing, check: https://github.com/Jade-ooju/spatial-understanding-vr

