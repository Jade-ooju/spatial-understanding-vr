#!/usr/bin/env python3
"""
Video Pipeline for VR Headset Videos
Integrates SAM 3 for object segmentation and VLM (Moondream2) for physical property analysis.

This script uses SAM 3 under the SAM License.
See SAM3_LICENSE in the repository root for license terms.
Copyright (c) Meta Platforms, Inc. and affiliates. All Rights Reserved.

Usage:
    python video_pipeline/video_pipeline.py --video resources/VR.mkv --prompt "spoon"
    python video_pipeline/video_pipeline.py --video resources/VR.mkv --prompt "spoon" --vlm-interval 30
"""

import argparse
import os
import sys
import time
import warnings
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
import torch

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    from sam3.model_builder import build_sam3_video_predictor
except ImportError:
    print("Error: SAM 3 not found. Make sure you're in the sam3 conda environment.")
    print("Activate with: conda activate sam3")
    sys.exit(1)

try:
    from physics_estimator import PhysicsEstimator
except ImportError:
    print("Warning: physics_estimator.py not found. Creating a placeholder.")
    print("Please create physics_estimator.py with a PhysicsEstimator class.")
    # Create a placeholder class
    class PhysicsEstimator:
        def __init__(self):
            self.initialized = False
            print("Using placeholder PhysicsEstimator. VLM analysis will be skipped.")
        
        def analyze(self, image: np.ndarray) -> Dict[str, str]:
            """Placeholder method. Returns mock results."""
            return {
                "material": "unknown (placeholder)",
                "weight": "unknown (placeholder)"
            }
    
    PhysicsEstimator = PhysicsEstimator


def check_environment():
    """Verify conda environment and dependencies."""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    if 'sam3' not in conda_env:
        print("WARNING: Not in 'sam3' conda environment!")
        print(f"Current environment: {conda_env}")
        print("Please activate: conda activate sam3")
        print()
    
    print("Environment check:")
    print(f"  Conda env: {conda_env}")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  CUDA device: {torch.cuda.get_device_name(0)}")
    print()


def apply_negative_mask(frame: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Apply negative masking: set background to black (RGB 0,0,0).
    
    Args:
        frame: Original frame (H, W, 3) in RGB
        mask: Binary mask (H, W) where True indicates object pixels
    
    Returns:
        Masked frame with black background
    """
    masked_frame = frame.copy()
    # Ensure mask is boolean and matches frame dimensions
    if mask.dtype != bool:
        mask = mask > 0.5
    
    # Set non-mask pixels to black
    masked_frame[~mask] = [0, 0, 0]
    return masked_frame


def extract_primary_mask(outputs: Dict, frame_idx: int) -> Optional[np.ndarray]:
    """
    Extract the primary mask from SAM 3 outputs for a given frame.
    
    Args:
        outputs: SAM 3 outputs dictionary
        frame_idx: Frame index
    
    Returns:
        Primary mask (H, W) or None if no mask found
    """
    if frame_idx not in outputs:
        return None
    
    frame_output = outputs[frame_idx]
    
    # Get masks and scores
    masks = frame_output.get("out_binary_masks", None)
    probs = frame_output.get("out_probs", None)
    obj_ids = frame_output.get("out_obj_ids", None)
    
    if masks is None:
        return None
    
    # Convert to numpy if needed (handles both tensor and numpy)
    if torch.is_tensor(masks):
        masks = masks.cpu().numpy()
    if isinstance(masks, np.ndarray) and masks.size == 0:
        return None
    if len(masks) == 0:
        return None
    
    # Convert probs if needed
    if probs is not None:
        if torch.is_tensor(probs):
            probs = probs.cpu().numpy()
        if isinstance(probs, np.ndarray) and probs.size == 0:
            probs = None
    
    # Select primary mask: highest confidence or largest area
    if probs is not None and len(probs) > 0:
        # Use highest confidence
        primary_idx = np.argmax(probs)
    else:
        # Use largest mask area
        mask_areas = []
        for mask in masks:
            if torch.is_tensor(mask):
                mask = mask.cpu().numpy()
            mask_areas.append(np.sum(mask))
        if len(mask_areas) == 0:
            return None
        primary_idx = np.argmax(mask_areas)
    
    primary_mask = masks[primary_idx]
    
    # Convert to numpy if still tensor
    if torch.is_tensor(primary_mask):
        primary_mask = primary_mask.cpu().numpy()
    
    # Ensure mask is 2D boolean
    if primary_mask.ndim > 2:
        primary_mask = primary_mask.squeeze()
    # Remove any extra dimensions
    while primary_mask.ndim > 2:
        primary_mask = primary_mask[0]
    
    if primary_mask.dtype != bool:
        primary_mask = primary_mask > 0.5
    
    return primary_mask


def draw_mask_contour(frame: np.ndarray, mask: np.ndarray, color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """
    Draw green contour on frame for the mask.
    
    Args:
        frame: Frame to draw on (BGR format for OpenCV)
        mask: Binary mask
        color: BGR color tuple (default: green)
    
    Returns:
        Annotated frame
    """
    annotated_frame = frame.copy()
    
    # Ensure mask is uint8
    if mask.dtype != np.uint8:
        mask_uint8 = (mask.astype(np.uint8) * 255)
    else:
        mask_uint8 = mask
    
    # Find contours
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours
    cv2.drawContours(annotated_frame, contours, -1, color, 2)
    
    return annotated_frame


def overlay_vlm_text(frame: np.ndarray, vlm_result: Dict[str, str], position: Tuple[int, int] = (10, 30)) -> np.ndarray:
    """
    Overlay VLM result text on frame.
    
    Args:
        frame: Frame to overlay text on (BGR format)
        vlm_result: Dictionary with 'material' and 'weight' keys
        position: Top-left position for text (x, y)
    
    Returns:
        Frame with text overlay
    """
    annotated_frame = frame.copy()
    
    # Prepare text
    material = vlm_result.get("material", "unknown")
    weight = vlm_result.get("weight", "unknown")
    
    text_lines = [
        f"Material: {material}",
        f"Weight: {weight}"
    ]
    
    # Draw text with background
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    line_height = 25
    
    for i, text in enumerate(text_lines):
        y = position[1] + i * line_height
        
        # Get text size for background rectangle
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        # Draw background rectangle
        cv2.rectangle(
            annotated_frame,
            (position[0] - 5, y - text_height - 5),
            (position[0] + text_width + 5, y + baseline + 5),
            (0, 0, 0),  # Black background
            -1
        )
        
        # Draw text
        cv2.putText(
            annotated_frame,
            text,
            (position[0], y),
            font,
            font_scale,
            (0, 255, 0),  # Green text
            thickness,
            cv2.LINE_AA
        )
    
    return annotated_frame


def ProcessVideo(
    video_path: str,
    text_prompt: str = "spoon",
    vlm_interval: int = 30,
    display: bool = True,
    output_path: Optional[str] = None,
    max_frames: Optional[int] = None,
) -> None:
    """
    Process video with SAM 3 and VLM analysis.
    
    Args:
        video_path: Path to video file (MP4, MKV, etc.) or JPEG folder
        text_prompt: Text prompt for SAM 3 (e.g., "spoon", "cup")
        vlm_interval: Run VLM every N frames (default: 30)
        display: Show real-time visualization (default: True)
        output_path: Optional path to save annotated video
    """
    print("=" * 70)
    print("SAM 3 + VLM Video Pipeline")
    print("=" * 70)
    print(f"Video: {video_path}")
    print(f"Text prompt: '{text_prompt}'")
    print(f"VLM interval: {vlm_interval} frames")
    print()
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"Error: Video not found: {video_path}")
        return
    
    # Initialize SAM 3 predictor
    print("1. Initializing SAM 3 video predictor...")
    start_time = time.time()
    try:
        predictor = build_sam3_video_predictor(gpus_to_use=[])
        elapsed = time.time() - start_time
        print(f"   ✓ SAM 3 predictor initialized ({elapsed:.2f} seconds)")
    except Exception as e:
        print(f"   ✗ Error initializing SAM 3: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Initialize VLM
    print("\n2. Initializing VLM (PhysicsEstimator)...")
    try:
        vlm_estimator = PhysicsEstimator()
        print("   ✓ VLM initialized")
    except Exception as e:
        print(f"   ✗ Error initializing VLM: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Load video with OpenCV for frame-by-frame access
    print(f"\n3. Loading video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"   ✗ Error: Could not open video file")
        return
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"   ✓ Video loaded: {width}x{height} @ {fps} FPS, {total_frames} frames")
    
    # Start SAM 3 session
    print(f"\n4. Starting SAM 3 session with video...")
    start_time = time.time()
    try:
        response = predictor.handle_request(
            request=dict(
                type="start_session",
                resource_path=video_path,
            )
        )
        session_id = response["session_id"]
        elapsed = time.time() - start_time
        print(f"   ✓ Session started: {session_id} ({elapsed:.2f} seconds)")
    except Exception as e:
        print(f"   ✗ Error starting session: {e}")
        import traceback
        traceback.print_exc()
        cap.release()
        return
    
    # Add text prompt on frame 0
    print(f"\n5. Adding text prompt '{text_prompt}' on frame 0...")
    try:
        response = predictor.handle_request(
            request=dict(
                type="add_prompt",
                session_id=session_id,
                frame_index=0,
                text=text_prompt,
            )
        )
        print(f"   ✓ Prompt added")
    except Exception as e:
        print(f"   ✗ Error adding prompt: {e}")
        import traceback
        traceback.print_exc()
        predictor.handle_request(dict(type="close_session", session_id=session_id))
        cap.release()
        return
    
    # Propagate through video to get all masks
    max_frames_to_track = max_frames if max_frames else total_frames
    if max_frames:
        print(f"\n6. Propagating through video (limited to {max_frames} frames, this may take a while)...")
    else:
        print(f"\n6. Propagating through video (this may take a while)...")
    outputs_per_frame = {}
    propagation_start = time.time()
    try:
        for response in predictor.handle_stream_request(
            request=dict(
                type="propagate_in_video",
                session_id=session_id,
                max_frame_num_to_track=max_frames_to_track,
            )
        ):
            frame_idx = response["frame_index"]
            outputs_per_frame[frame_idx] = response["outputs"]
            if (frame_idx + 1) % 50 == 0:
                elapsed = time.time() - propagation_start
                fps = (frame_idx + 1) / elapsed if elapsed > 0 else 0
                print(f"   Processed {frame_idx + 1}/{max_frames_to_track} frames... ({elapsed:.1f}s elapsed, {fps:.2f} frames/sec)")
        propagation_elapsed = time.time() - propagation_start
        print(f"   ✓ Propagation complete: {len(outputs_per_frame)} frames processed ({propagation_elapsed:.2f} seconds, {len(outputs_per_frame)/propagation_elapsed:.2f} frames/sec)")
    except Exception as e:
        print(f"   ✗ Error during propagation: {e}")
        import traceback
        traceback.print_exc()
        predictor.handle_request(dict(type="close_session", session_id=session_id))
        cap.release()
        return
    
    # Prepare video writer if output path is specified
    video_writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"\n7. Video writer initialized: {output_path}")
    
    # Process frames
    print(f"\n8. Processing frames and displaying results...")
    print("   Press 'q' to quit, 'p' to pause")
    
    # Reset video capture to beginning
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Limit total frames if max_frames is set
    frames_to_process = max_frames_to_track if max_frames else total_frames
    
    frame_count = 0
    last_vlm_result = {"material": "analyzing...", "weight": "analyzing..."}
    last_vlm_frame = -vlm_interval  # Force VLM on first frame
    paused = False
    processing_start = time.time()
    vlm_times = []
    
    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret or frame_count >= frames_to_process:
                    break
                
                # Convert BGR to RGB for processing
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Get mask from SAM 3 outputs
                mask = extract_primary_mask(outputs_per_frame, frame_count)
                
                if mask is not None:
                    # Apply negative masking for VLM
                    masked_frame_rgb = apply_negative_mask(frame_rgb, mask)
                    
                    # Run VLM every N frames or on first frame
                    if (frame_count - last_vlm_frame) >= vlm_interval:
                        try:
                            vlm_start = time.time()
                            # Convert RGB to PIL Image format (numpy array)
                            last_vlm_result = vlm_estimator.analyze(masked_frame_rgb)
                            vlm_elapsed = time.time() - vlm_start
                            vlm_times.append(vlm_elapsed)
                            last_vlm_frame = frame_count
                            print(f"   Frame {frame_count}: VLM result - {last_vlm_result} ({vlm_elapsed:.2f}s)")
                        except Exception as e:
                            print(f"   Frame {frame_count}: VLM error (using cached result): {e}")
                    
                    # Draw green contour
                    annotated_frame = draw_mask_contour(frame, mask)
                    
                    # Overlay VLM text
                    annotated_frame = overlay_vlm_text(annotated_frame, last_vlm_result)
                else:
                    # No mask found, show raw frame
                    annotated_frame = frame.copy()
                    # Still show VLM result if available
                    if frame_count - last_vlm_frame < vlm_interval:
                        annotated_frame = overlay_vlm_text(annotated_frame, last_vlm_result)
                
                # Display frame
                if display:
                    cv2.imshow("SAM 3 + VLM Video Pipeline", annotated_frame)
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("\n   Quitting...")
                        break
                    elif key == ord('p'):
                        paused = True
                        print("\n   Paused. Press 'p' to resume, 'q' to quit")
                
                # Write frame if output path specified
                if video_writer:
                    video_writer.write(annotated_frame)
                
                frame_count += 1
            else:
                # Paused state
                key = cv2.waitKey(100) & 0xFF
                if key == ord('p'):
                    paused = False
                    print("   Resumed")
                elif key == ord('q'):
                    print("\n   Quitting...")
                    break
        
        processing_elapsed = time.time() - processing_start
        print(f"\n   ✓ Processed {frame_count} frames ({processing_elapsed:.2f} seconds, {frame_count/processing_elapsed:.2f} frames/sec)")
        if vlm_times:
            print(f"   VLM analysis: {len(vlm_times)} calls, avg {np.mean(vlm_times):.2f}s per call, total {np.sum(vlm_times):.2f}s")
    
    except KeyboardInterrupt:
        print("\n   Interrupted by user")
    finally:
        # Cleanup
        if video_writer:
            video_writer.release()
            print(f"\n9. Output video saved: {output_path}")
        
        if display:
            cv2.destroyAllWindows()
        
        cap.release()
        
        # Close SAM 3 session
        print("\n10. Closing SAM 3 session...")
        try:
            predictor.handle_request(
                request=dict(
                    type="close_session",
                    session_id=session_id,
                )
            )
            print("   ✓ Session closed")
        except Exception as e:
            print(f"   ⚠ Error closing session: {e}")
    
    print("\n" + "=" * 70)
    print("✓ Complete!")
    print("=" * 70)


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Process VR videos with SAM 3 and VLM for object segmentation and physical property analysis"
    )
    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Path to video file (MP4, MKV, etc.) or JPEG folder"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="spoon",
        help="Text prompt for SAM 3 (default: 'spoon')"
    )
    parser.add_argument(
        "--vlm-interval",
        type=int,
        default=30,
        help="Run VLM every N frames (default: 30)"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Disable real-time display (useful for headless systems)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to save annotated video"
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Limit processing to first N frames (useful for testing)"
    )
    
    args = parser.parse_args()
    
    # Check environment
    check_environment()
    
    # Run pipeline
    ProcessVideo(
        video_path=args.video,
        text_prompt=args.prompt,
        vlm_interval=args.vlm_interval,
        display=not args.no_display,
        output_path=args.output,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    main()

