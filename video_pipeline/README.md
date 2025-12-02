# Video Pipeline Scripts

This directory contains the scripts for the SAM 3 + VLM Video Pipeline.

## Files

### video_pipeline.py
Main pipeline script that processes videos with SAM 3 and VLM analysis.

**Usage**:
```bash
python scripts/video_pipeline/video_pipeline.py \
  --video <video_path> \
  --prompt "<text_prompt>" \
  --output <output_path>
```

**Features**:
- SAM 3 object segmentation
- Negative masking (black background)
- VLM physical property analysis
- Real-time visualization
- Timing information

### physics_estimator.py
VLM wrapper class for physical property analysis.

**Features**:
- Moondream2 integration support
- Placeholder mode when VLM not available
- Material and weight analysis

**Usage**:
```python
from physics_estimator import PhysicsEstimator

estimator = PhysicsEstimator()
result = estimator.analyze(image_with_black_bg)
# Returns: {"material": "...", "weight": "..."}
```

### monitor_progress.sh
Utility script to monitor pipeline progress.

**Usage**:
```bash
./scripts/video_pipeline/monitor_progress.sh
```

Shows:
- Current progress
- Timing summary
- Output file status
- Process status

## Dependencies

- SAM 3 (installed in conda environment)
- OpenCV (`opencv-python`)
- PyTorch
- NumPy
- Moondream2 (optional, for VLM): `pip install transformers torch`

## Documentation

See [docs/video_pipeline/](../../docs/video_pipeline/) for complete documentation.

