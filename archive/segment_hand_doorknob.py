#!/usr/bin/env python3
"""
Segment hand and metal door knob from video/image using SAM 3.

This script uses SAM 3 under the SAM License.
See SAM3_LICENSE in the repository root for license terms.
Copyright (c) Meta Platforms, Inc. and affiliates. All Rights Reserved.

Usage:
    # Test on single image first
    python video_pipeline/segment_hand_doorknob.py --image resources/Doorknob.png
    
    # Process video
    python video_pipeline/segment_hand_doorknob.py --video resources/Red_Door.mp4 --output outputs/red_door_segmented.mp4
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
from PIL import Image

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    from sam3.model_builder import build_sam3_video_predictor, build_sam3_image_model
    from sam3.model.sam3_image_processor import Sam3Processor
except ImportError:
    print("Error: SAM 3 not found. Make sure you're in the sam3 conda environment.")
    print("Activate with: conda activate sam3")
    sys.exit(1)

try:
    from multi_object_detector import detect_hands_and_object, extract_primary_mask
except ImportError:
    print("Error: multi_object_detector.py not found.")
    sys.exit(1)

# Define visualization functions locally (reused from video_pipeline.py)
def apply_color_mask(frame: np.ndarray, mask: np.ndarray, color: Tuple[int, int, int], alpha: float = 0.5) -> np.ndarray:
    """Apply semi-transparent color mask overlay."""
    overlay = frame.copy()
    if mask.dtype != bool:
        mask = mask > 0.5
    color_mask = np.zeros_like(frame)
    color_mask[mask] = color
    result = cv2.addWeighted(overlay, 1.0 - alpha, color_mask, alpha, 0)
    return result


def draw_mask_contour(frame: np.ndarray, mask: np.ndarray, color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """Draw contour on frame for the mask."""
    annotated_frame = frame.copy()
    if mask.dtype != np.uint8:
        mask_uint8 = (mask.astype(np.uint8) * 255)
    else:
        mask_uint8 = mask
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(annotated_frame, contours, -1, color, 3)
    return annotated_frame


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


def visualize_segmented_image(
    frame: np.ndarray,
    hand_mask: Optional[np.ndarray],
    doorknob_mask: Optional[np.ndarray],
    hand_color: Tuple[int, int, int] = (255, 255, 0),  # Cyan in BGR
    doorknob_color: Tuple[int, int, int] = (255, 0, 255),  # Magenta in BGR
    alpha: float = 0.6,
    contours_only: bool = False,
) -> np.ndarray:
    """
    Visualize hand and door knob masks with very visible colors.
    
    Args:
        frame: Original frame (BGR format)
        hand_mask: Binary mask for hand (optional)
        doorknob_mask: Binary mask for door knob (optional)
        hand_color: BGR color for hand (default: cyan)
        doorknob_color: BGR color for door knob (default: magenta)
        alpha: Transparency for masks (default: 0.6 for high visibility)
        contours_only: If True, only draw contours without overlay (default: False)
    
    Returns:
        Frame with all masks overlaid
    """
    annotated_frame = frame.copy()
    
    # Apply hand mask if available
    if hand_mask is not None:
        if not contours_only:
            annotated_frame = apply_color_mask(annotated_frame, hand_mask, hand_color, alpha)
        annotated_frame = draw_mask_contour(annotated_frame, hand_mask, hand_color)
    
    # Apply door knob mask if available
    if doorknob_mask is not None:
        if not contours_only:
            annotated_frame = apply_color_mask(annotated_frame, doorknob_mask, doorknob_color, alpha)
        annotated_frame = draw_mask_contour(annotated_frame, doorknob_mask, doorknob_color)
    
    return annotated_frame


def process_image(
    image_path: str,
    hand_prompt: str = "hand",
    doorknob_prompt: str = "metal door knob",
    output_path: Optional[str] = None,
) -> None:
    """
    Process a single image to segment hand and door knob.
    
    Args:
        image_path: Path to input image
        hand_prompt: Text prompt for hand detection
        doorknob_prompt: Text prompt for door knob detection
        output_path: Optional output path (default: outputs/doorknob_segmented.png)
    """
    print("=" * 70)
    print("SAM 3 Image Segmentation: Hand + Metal Door Knob")
    print("=" * 70)
    print(f"Image: {image_path}")
    print(f"Hand prompt: '{hand_prompt}'")
    print(f"Door knob prompt: '{doorknob_prompt}'")
    print()
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return
    
    # Set default output path
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}_segmented.png")
    
    # Load image
    print("1. Loading image...")
    try:
        image = Image.open(image_path).convert("RGB")
        image_array = np.array(image)
        print(f"   ✓ Image loaded: {image_array.shape[1]}x{image_array.shape[0]}")
    except Exception as e:
        print(f"   ✗ Error loading image: {e}")
        return
    
    # Initialize SAM 3 image model
    print("\n2. Initializing SAM 3 image model...")
    start_time = time.time()
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = build_sam3_image_model(device=device)
        processor = Sam3Processor(model, device=device, confidence_threshold=0.5)
        elapsed = time.time() - start_time
        print(f"   ✓ SAM 3 model initialized ({elapsed:.2f} seconds)")
        print(f"   Using device: {device}")
    except Exception as e:
        print(f"   ✗ Error initializing SAM 3: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Segment hand
    print(f"\n3. Segmenting hand with prompt: '{hand_prompt}'")
    hand_mask = None
    try:
        state = processor.set_image(image)
        state = processor.set_text_prompt(hand_prompt, state)
        masks = state.get("masks", None)
        if masks is not None and len(masks) > 0:
            # Get primary mask (highest confidence)
            hand_mask = masks[0]
            if torch.is_tensor(hand_mask):
                hand_mask = hand_mask.cpu().numpy()
            # Ensure 2D
            if hand_mask.ndim > 2:
                hand_mask = hand_mask.squeeze()
            if hand_mask.dtype != bool:
                hand_mask = hand_mask > 0.5
            print(f"   ✓ Hand detected")
        else:
            print(f"   ⚠ No hand detected")
    except Exception as e:
        print(f"   ✗ Error segmenting hand: {e}")
        import traceback
        traceback.print_exc()
    
    # Segment door knob
    print(f"\n4. Segmenting door knob with prompt: '{doorknob_prompt}'")
    doorknob_mask = None
    try:
        state = processor.set_image(image)
        state = processor.set_text_prompt(doorknob_prompt, state)
        masks = state.get("masks", None)
        if masks is not None and len(masks) > 0:
            # Get primary mask (highest confidence)
            doorknob_mask = masks[0]
            if torch.is_tensor(doorknob_mask):
                doorknob_mask = doorknob_mask.cpu().numpy()
            # Ensure 2D
            if doorknob_mask.ndim > 2:
                doorknob_mask = doorknob_mask.squeeze()
            if doorknob_mask.dtype != bool:
                doorknob_mask = doorknob_mask > 0.5
            print(f"   ✓ Door knob detected")
        else:
            print(f"   ⚠ No door knob detected")
    except Exception as e:
        print(f"   ✗ Error segmenting door knob: {e}")
        import traceback
        traceback.print_exc()
    
    # Visualize results
    print(f"\n5. Creating visualization...")
    try:
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Apply very visible colors
        HAND_COLOR = (255, 255, 0)  # Cyan in BGR
        DOORKNOB_COLOR = (255, 0, 255)  # Magenta in BGR
        
        annotated_frame = visualize_segmented_image(
            frame_bgr,
            hand_mask,
            doorknob_mask,
            hand_color=HAND_COLOR,
            doorknob_color=DOORKNOB_COLOR,
            alpha=0.6,  # High visibility
        )
        
        # Convert back to RGB for saving
        annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        annotated_image = Image.fromarray(annotated_rgb)
        annotated_image.save(output_path)
        print(f"   ✓ Visualization saved to: {output_path}")
    except Exception as e:
        print(f"   ✗ Error creating visualization: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 70)
    print("✓ Image segmentation complete!")
    print("=" * 70)


def process_video(
    video_path: str,
    hand_prompt: str = "hand",
    doorknob_prompt: str = "metal door knob",
    output_path: Optional[str] = None,
    max_frames: Optional[int] = None,
    contours_only: bool = False,
) -> None:
    """
    Process video to segment hand and door knob in all frames.
    
    Args:
        video_path: Path to input video
        hand_prompt: Text prompt for hand detection
        doorknob_prompt: Text prompt for door knob detection
        output_path: Optional output path (default: outputs/red_door_segmented.mp4)
        max_frames: Optional limit on number of frames to process
    """
    print("=" * 70)
    print("SAM 3 Video Segmentation: Hand + Metal Door Knob")
    print("=" * 70)
    print(f"Video: {video_path}")
    print(f"Hand prompt: '{hand_prompt}'")
    print(f"Door knob prompt: '{doorknob_prompt}'")
    print()
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"Error: Video not found: {video_path}")
        return
    
    # Set default output path
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        suffix = "_contours_only" if contours_only else "_segmented"
        output_path = os.path.join(output_dir, f"{base_name}{suffix}.mp4")
    
    # Initialize SAM 3 video predictor
    print("1. Initializing SAM 3 video predictor...")
    start_time = time.time()
    try:
        if torch.cuda.is_available():
            gpus_to_use = [0]
            print(f"   Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            gpus_to_use = []
        from sam3.model_builder import build_sam3_video_predictor
        predictor = build_sam3_video_predictor(gpus_to_use=gpus_to_use)
        elapsed = time.time() - start_time
        print(f"   ✓ SAM 3 predictor initialized ({elapsed:.2f} seconds)")
    except Exception as e:
        print(f"   ✗ Error initializing SAM 3: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Load video with OpenCV
    print(f"\n2. Loading video: {video_path}")
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
    cap.release()
    
    # Detect hands and door knob
    print(f"\n3. Detecting hands and door knob with SAM 3...")
    max_frames_to_track = max_frames if max_frames else total_frames
    try:
        masks_dict = detect_hands_and_object(
            video_path=video_path,
            object_prompt=doorknob_prompt,
            predictor=predictor,
            max_frames=max_frames_to_track,
        )
        hands_masks = masks_dict["hands"]
        doorknob_masks = masks_dict["object"]
        print(f"   ✓ Detection complete")
        print(f"      Hands: {len([m for m in hands_masks.values() if m is not None])} frames with detection")
        print(f"      Door knob: {len([m for m in doorknob_masks.values() if m is not None])} frames with detection")
    except Exception as e:
        print(f"   ✗ Error in detection: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Prepare video writer
    print(f"\n4. Initializing video writer: {output_path}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    if not video_writer.isOpened():
        print(f"   ✗ Error: Could not initialize video writer")
        return
    print(f"   ✓ Video writer ready")
    
    # Process frames
    print(f"\n5. Processing frames and saving to video...")
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    frames_to_process = max_frames_to_track if max_frames else total_frames
    
    frame_count = 0
    processing_start = time.time()
    
    # Color definitions - very visible
    HAND_COLOR = (255, 255, 0)  # Cyan in BGR
    DOORKNOB_COLOR = (255, 0, 255)  # Magenta in BGR
    
    try:
        while frame_count < frames_to_process:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Get masks for current frame
            hand_mask = hands_masks.get(frame_count)
            doorknob_mask = doorknob_masks.get(frame_count)
            
            # Visualize with very visible colors
            annotated_frame = visualize_segmented_image(
                frame,
                hand_mask,
                doorknob_mask,
                hand_color=HAND_COLOR,
                doorknob_color=DOORKNOB_COLOR,
                alpha=0.6,  # High visibility
                contours_only=contours_only,
            )
            
            # Write frame
            video_writer.write(annotated_frame)
            
            frame_count += 1
            if (frame_count + 1) % 50 == 0:
                elapsed = time.time() - processing_start
                fps_current = frame_count / elapsed if elapsed > 0 else 0
                print(f"   Processed {frame_count + 1}/{frames_to_process} frames ({fps_current:.1f} fps)")
        
        processing_elapsed = time.time() - processing_start
        print(f"\n   ✓ Processed {frame_count} frames ({processing_elapsed:.2f} seconds, {frame_count/processing_elapsed:.2f} frames/sec)")
    
    except KeyboardInterrupt:
        print("\n   Interrupted by user")
    finally:
        video_writer.release()
        cap.release()
    
    print(f"\n6. Output video saved: {output_path}")
    print("\n" + "=" * 70)
    print("✓ Video segmentation complete!")
    print("=" * 70)


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Segment hand and metal door knob from images/videos using SAM 3"
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Path to input image (for single image processing)"
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to input video (for video processing)"
    )
    parser.add_argument(
        "--hand-prompt",
        type=str,
        default="hand",
        help="Text prompt for hand detection (default: 'hand')"
    )
    parser.add_argument(
        "--doorknob-prompt",
        type=str,
        default="metal door knob",
        help="Text prompt for door knob detection (default: 'metal door knob')"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path (default: auto-generated in outputs/)"
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Limit processing to first N frames (for video, useful for testing)"
    )
    parser.add_argument(
        "--contours-only",
        action="store_true",
        help="Only draw segmentation contours without semi-transparent overlay (keeps background unchanged)"
    )
    
    args = parser.parse_args()
    
    # Check that either image or video is provided
    if not args.image and not args.video:
        parser.error("Either --image or --video must be provided")
    
    if args.image and args.video:
        parser.error("Please provide either --image or --video, not both")
    
    # Check environment
    check_environment()
    
    # Process based on input type
    if args.image:
        process_image(
            image_path=args.image,
            hand_prompt=args.hand_prompt,
            doorknob_prompt=args.doorknob_prompt,
            output_path=args.output,
        )
    elif args.video:
        process_video(
            video_path=args.video,
            hand_prompt=args.hand_prompt,
            doorknob_prompt=args.doorknob_prompt,
            output_path=args.output,
            max_frames=args.max_frames,
            contours_only=args.contours_only,
        )


if __name__ == "__main__":
    main()

