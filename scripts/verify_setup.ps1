# Verification Script for SAM 3 + VLM Setup
# Run this script to verify your installation

$ErrorActionPreference = "Continue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Verification Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Check 1: Conda environment
Write-Host "1. Checking conda environment..." -ForegroundColor Yellow
$condaEnv = $env:CONDA_DEFAULT_ENV
if ($condaEnv -eq "sam3") {
    Write-Host "   ✓ Conda environment: $condaEnv" -ForegroundColor Green
} else {
    Write-Host "   ✗ Not in 'sam3' environment. Current: $condaEnv" -ForegroundColor Red
    Write-Host "     Run: conda activate sam3" -ForegroundColor Yellow
    $allPassed = $false
}

# Check 2: GPU/CUDA
Write-Host ""
Write-Host "2. Checking GPU/CUDA..." -ForegroundColor Yellow
try {
    python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')" 2>&1 | Out-Null
    $cudaCheck = python -c "import torch; print('CUDA:', torch.cuda.is_available())" 2>&1
    if ($cudaCheck -like "*True*") {
        $gpuName = python -c "import torch; print(torch.cuda.get_device_name(0))" 2>&1
        Write-Host "   ✓ CUDA available: True" -ForegroundColor Green
        Write-Host "   ✓ GPU: $gpuName" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ CUDA not available (will run on CPU - very slow)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ Error checking CUDA: $_" -ForegroundColor Red
    $allPassed = $false
}

# Check 3: SAM 3
Write-Host ""
Write-Host "3. Checking SAM 3..." -ForegroundColor Yellow
try {
    $samCheck = python -c "from sam3.model_builder import build_sam3_video_predictor; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ SAM 3 installed successfully" -ForegroundColor Green
    } else {
        Write-Host "   ✗ SAM 3 import failed: $samCheck" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "   ✗ SAM 3 not found. Error: $_" -ForegroundColor Red
    Write-Host "     Install with: cd ..\..\SAM ; pip install -e ." -ForegroundColor Yellow
    $allPassed = $false
}

# Check 4: VLM (PhysicsEstimator)
Write-Host ""
Write-Host "4. Checking VLM (PhysicsEstimator)..." -ForegroundColor Yellow
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VLMTest = @"
import sys
sys.path.insert(0, r'$ProjectRoot\video_pipeline')
try:
    from physics_estimator import PhysicsEstimator
    est = PhysicsEstimator()
    print('OK:', est.initialized)
except Exception as e:
    print('ERROR:', str(e))
"@

try {
    $vlmResult = $VLMTest | python 2>&1
    if ($vlmResult -like "*OK: True*") {
        Write-Host "   ✓ VLM initialized successfully" -ForegroundColor Green
    } elseif ($vlmResult -like "*OK: False*") {
        Write-Host "   ⚠ VLM found but not initialized (may need Hugging Face auth)" -ForegroundColor Yellow
    } else {
        Write-Host "   ✗ VLM error: $vlmResult" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "   ✗ VLM check failed: $_" -ForegroundColor Red
    $allPassed = $false
}

# Check 5: Project dependencies
Write-Host ""
Write-Host "5. Checking project dependencies..." -ForegroundColor Yellow
$deps = @("cv2", "numpy", "tqdm")
$depsOk = $true
foreach ($dep in $deps) {
    try {
        python -c "import $dep; print('OK')" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ $dep" -ForegroundColor Green
        } else {
            Write-Host "   ✗ $dep not found" -ForegroundColor Red
            $depsOk = $false
            $allPassed = $false
        }
    } catch {
        Write-Host "   ✗ $dep not found" -ForegroundColor Red
        $depsOk = $false
        $allPassed = $false
    }
}

# Check 6: SAM 3 repository location
Write-Host ""
Write-Host "6. Checking SAM 3 repository..." -ForegroundColor Yellow
$SAMDir = Join-Path (Split-Path -Parent $ProjectRoot) "SAM"
if (Test-Path $SAMDir) {
    if (Test-Path (Join-Path $SAMDir ".git")) {
        Write-Host "   ✓ SAM 3 repository found at: $SAMDir" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ SAM directory exists but is not a git repository" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ SAM 3 repository not found at: $SAMDir" -ForegroundColor Red
    $allPassed = $false
}

# Check 7: Conda environment location
Write-Host ""
Write-Host "7. Checking conda environment location..." -ForegroundColor Yellow
$condaInfo = conda info --json | ConvertFrom-Json
$envsDirs = $condaInfo.envs_dirs
$envPath = $envsDirs | Where-Object { $_ -like "*sam3*" -or (Test-Path (Join-Path $_ "sam3")) }
if ($envPath) {
    Write-Host "   ✓ Conda envs directories: $($envsDirs -join ', ')" -ForegroundColor Green
    $sam3EnvPath = $envsDirs | ForEach-Object { Join-Path $_ "sam3" } | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($sam3EnvPath) {
        Write-Host "   ✓ sam3 environment found at: $sam3EnvPath" -ForegroundColor Green
        if ($sam3EnvPath -like "D:*") {
            Write-Host "   ✓ Environment is on D drive as requested" -ForegroundColor Green
        } else {
            Write-Host "   ⚠ Environment is not on D drive: $sam3EnvPath" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   ⚠ Could not determine environment location" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "✓ All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You're ready to run the pipeline:" -ForegroundColor Yellow
    Write-Host "  python video_pipeline/video_pipeline.py --video resources/video.mp4 --prompt `"spoon`"" -ForegroundColor White
} else {
    Write-Host "✗ Some checks failed. Please review the errors above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  - Activate environment: conda activate sam3" -ForegroundColor White
    Write-Host "  - Install SAM 3: cd ..\..\SAM ; pip install -e ." -ForegroundColor White
    Write-Host "  - Install dependencies: pip install opencv-python numpy tqdm transformers" -ForegroundColor White
}
Write-Host "==========================================" -ForegroundColor Cyan



