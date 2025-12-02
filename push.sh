#!/bin/bash
# Quick push script for spatial-understanding-vr

cd "$(dirname "$0")"

echo "=== Pushing to GitHub ==="
echo ""

# Check if already has remote
if git remote | grep -q origin; then
    echo "Remote 'origin' already exists. Updating..."
    git remote set-url origin https://github.com/Jade-ooju/spatial-understanding-vr.git
else
    echo "Adding remote..."
    git remote add origin https://github.com/Jade-ooju/spatial-understanding-vr.git
fi

echo ""
echo "=== Staging files ==="
git add .

echo ""
echo "=== Creating commit ==="
git commit -m "Initial commit: Video pipeline for VR spatial understanding with SAM 3 and VLM"

echo ""
echo "=== Setting branch to main ==="
git branch -M main

echo ""
echo "=== Pushing to GitHub ==="
echo "You may be prompted for credentials..."
git push -u origin main

echo ""
echo "✅ Done! Check: https://github.com/Jade-ooju/spatial-understanding-vr"
