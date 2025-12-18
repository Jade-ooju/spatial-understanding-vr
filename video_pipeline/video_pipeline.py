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
                "weight": "unknown (placeholder)",
                "situation": "unknown (placeholder)"
            }
    
    PhysicsEstimator = PhysicsEstimator

try:
    from multi_object_detector import detect_hands_and_object
except ImportError:
    print("Warning: multi_object_detector.py not found. Multi-object detection will be disabled.")
    def detect_hands_and_object(*args, **kwargs):
        return {"hands": {}, "object": {}}


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


def apply_color_mask(frame: np.ndarray, mask: np.ndarray, color: Tuple[int, int, int], alpha: float = 0.4) -> np.ndarray:
    """
    Apply semi-transparent fluorescent color mask overlay.
    
    Args:
        frame: Frame to overlay mask on (BGR format)
        mask: Binary mask (H, W)
        color: BGR color tuple for the mask
        alpha: Transparency value (0.0 = transparent, 1.0 = opaque)
    
    Returns:
        Frame with colored mask overlay
    """
    overlay = frame.copy()
    
    # Ensure mask is boolean
    if mask.dtype != bool:
        mask = mask > 0.5
    
    # Create color mask
    color_mask = np.zeros_like(frame)
    color_mask[mask] = color
    
    # Blend with original frame
    result = cv2.addWeighted(overlay, 1.0 - alpha, color_mask, alpha, 0)
    
    return result


def visualize_multi_object_masks(
    frame: np.ndarray,
    hand_mask: Optional[np.ndarray],
    object_mask: Optional[np.ndarray],
    hand_color: Tuple[int, int, int] = (255, 255, 0),  # Cyan in BGR
    object_color: Tuple[int, int, int] = (0, 255, 0),  # Green in BGR
    alpha: float = 0.4,
    draw_contours: bool = True,
) -> np.ndarray:
    """
    Visualize multiple object masks with fluorescent colors.
    
    Args:
        frame: Original frame (BGR format)
        hand_mask: Binary mask for hands (optional)
        object_mask: Binary mask for target object (optional)
        hand_color: BGR color for hands (default: cyan)
        object_color: BGR color for object (default: green)
        alpha: Transparency for masks (default: 0.4)
        draw_contours: Whether to draw contour lines (default: True)
    
    Returns:
        Frame with all masks overlaid
    """
    annotated_frame = frame.copy()
    
    # Apply hand mask if available
    if hand_mask is not None:
        annotated_frame = apply_color_mask(annotated_frame, hand_mask, hand_color, alpha)
        if draw_contours:
            annotated_frame = draw_mask_contour(annotated_frame, hand_mask, hand_color)
    
    # Apply object mask if available
    if object_mask is not None:
        annotated_frame = apply_color_mask(annotated_frame, object_mask, object_color, alpha)
        if draw_contours:
            annotated_frame = draw_mask_contour(annotated_frame, object_mask, object_color)
    
    return annotated_frame


def draw_wireframe_2d(
    frame: np.ndarray,
    mask: np.ndarray,
    color: Tuple[int, int, int] = (255, 255, 255),  # White in BGR
    line_thickness: int = 1,
    point_skip: int = 5,
) -> np.ndarray:
    """
    Draw 2D wireframe from mask contour (sparse line representation).
    
    Args:
        frame: Frame to draw on (BGR format)
        mask: Binary mask
        color: BGR color for wireframe (default: white)
        line_thickness: Thickness of wireframe lines
        point_skip: Draw every Nth contour point (for sparse wireframe)
    
    Returns:
        Frame with wireframe overlay
    """
    annotated_frame = frame.copy()
    
    # Ensure mask is uint8
    if mask.dtype != np.uint8:
        mask_uint8 = (mask.astype(np.uint8) * 255)
    else:
        mask_uint8 = mask
    
    # Find contours
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw wireframe (sparse lines connecting contour points)
    for contour in contours:
        if len(contour) < 2:
            continue
        
        # Draw lines connecting every Nth point
        points = contour.reshape(-1, 2)
        for i in range(0, len(points) - point_skip, point_skip):
            pt1 = tuple(points[i])
            pt2 = tuple(points[i + point_skip])
            cv2.line(annotated_frame, pt1, pt2, color, line_thickness)
        
        # Connect last point to first to close the loop
        if len(points) > point_skip:
            cv2.line(annotated_frame, tuple(points[-1]), tuple(points[0]), color, line_thickness)
    
    return annotated_frame


def draw_estimated_3d_box(
    frame: np.ndarray,
    mask: np.ndarray,
    color: Tuple[int, int, int] = (255, 255, 255),  # White in BGR
    line_thickness: int = 1,
) -> np.ndarray:
    """
    Draw estimated 3D bounding box wireframe from mask.
    Estimates depth from mask area and projects 3D box to 2D.
    
    Args:
        frame: Frame to draw on (BGR format)
        mask: Binary mask
        color: BGR color for wireframe (default: white)
        line_thickness: Thickness of wireframe lines
    
    Returns:
        Frame with 3D box wireframe overlay
    """
    annotated_frame = frame.copy()
    
    # Get mask bounding box
    if mask.dtype != np.uint8:
        mask_uint8 = (mask.astype(np.uint8) * 255)
    else:
        mask_uint8 = mask
    
    # Find bounding box
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return annotated_frame
    
    # Get largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Estimate depth from mask area (larger area = closer = smaller depth)
    mask_area = cv2.contourArea(largest_contour)
    frame_area = frame.shape[0] * frame.shape[1]
    area_ratio = mask_area / frame_area if frame_area > 0 else 0
    
    # Estimate depth (0.1 to 0.5 of box width, based on area ratio)
    estimated_depth = w * (0.1 + 0.4 * (1 - area_ratio))
    
    # Define 3D box corners (in image coordinates)
    # Front face (z = 0)
    front_corners = np.array([
        [x, y],           # Top-left
        [x + w, y],       # Top-right
        [x + w, y + h],   # Bottom-right
        [x, y + h],       # Bottom-left
    ], dtype=np.float32)
    
    # Back face (z = estimated_depth, shifted slightly)
    depth_offset = estimated_depth * 0.3  # Shift back face
    back_corners = front_corners.copy()
    back_corners[:, 0] += depth_offset  # Shift right
    back_corners[:, 1] -= depth_offset * 0.5  # Shift up slightly
    
    # Draw front face
    for i in range(4):
        pt1 = tuple(front_corners[i].astype(int))
        pt2 = tuple(front_corners[(i + 1) % 4].astype(int))
        cv2.line(annotated_frame, pt1, pt2, color, line_thickness)
    
    # Draw back face
    for i in range(4):
        pt1 = tuple(back_corners[i].astype(int))
        pt2 = tuple(back_corners[(i + 1) % 4].astype(int))
        cv2.line(annotated_frame, pt1, pt2, color, line_thickness)
    
    # Draw connecting edges
    for i in range(4):
        pt1 = tuple(front_corners[i].astype(int))
        pt2 = tuple(back_corners[i].astype(int))
        cv2.line(annotated_frame, pt1, pt2, color, line_thickness)
    
    return annotated_frame


def draw_pill_background(
    frame: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    color: Tuple[int, int, int] = (0, 0, 0),
    alpha: float = 0.7,
    border_color: Tuple[int, int, int] = (255, 255, 255),
    border_thickness: int = 1,
) -> np.ndarray:
    """
    Draw a semi-transparent pill/capsule-shaped background.
    
    Args:
        frame: Frame to draw on (BGR format)
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Width of the pill
        height: Height of the pill
        color: BGR color for background
        alpha: Transparency (0.0 = transparent, 1.0 = opaque)
        border_color: BGR color for border
        border_thickness: Thickness of border
    
    Returns:
        Frame with pill background
    """
    annotated_frame = frame.copy()
    overlay = annotated_frame.copy()
    
    # Calculate radius for rounded ends (half of height)
    radius = height // 2
    
    # Draw filled rounded rectangle (pill shape)
    # Main rectangle body
    cv2.rectangle(
        overlay,
        (x + radius, y),
        (x + width - radius, y + height),
        color,
        -1
    )
    # Draw left rounded end (semi-circle)
    cv2.ellipse(overlay, (x + radius, y + radius), (radius, radius), 180, 0, 180, color, -1)
    # Draw right rounded end (semi-circle)
    cv2.ellipse(overlay, (x + width - radius, y + radius), (radius, radius), 0, 0, 180, color, -1)
    
    # Apply transparency to background
    cv2.addWeighted(overlay, alpha, annotated_frame, 1.0 - alpha, 0, annotated_frame)
    
    # Draw border directly on final frame (after transparency is applied)
    # Top and bottom lines
    cv2.line(annotated_frame, (x + radius, y), (x + width - radius, y), border_color, border_thickness)
    cv2.line(annotated_frame, (x + radius, y + height), (x + width - radius, y + height), border_color, border_thickness)
    # Left arc (semi-circle)
    cv2.ellipse(annotated_frame, (x + radius, y + radius), (radius, radius), 180, 0, 180, border_color, border_thickness)
    # Right arc (semi-circle)
    cv2.ellipse(annotated_frame, (x + width - radius, y + radius), (radius, radius), 0, 0, 180, border_color, border_thickness)
    
    return annotated_frame


def draw_system_header(
    frame: np.ndarray,
    frame_count: int,
    fps: float,
    position: Tuple[int, int] = (10, 10),
) -> np.ndarray:
    """
    Draw system header with REC indicator, frame count, and FPS.
    
    Args:
        frame: Frame to overlay on (BGR format)
        frame_count: Current frame number
        fps: Current FPS value
        position: Top-left position (x, y)
    
    Returns:
        Frame with system header
    """
    annotated_frame = frame.copy()
    
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 1
    line_type = cv2.LINE_AA
    
    # Text content
    rec_text = "● REC"
    frame_text = f"FRAME: {frame_count}"
    fps_text = f"FPS: {fps:.1f}"
    
    # Get text sizes
    (rec_w, rec_h), _ = cv2.getTextSize(rec_text, font, font_scale, thickness)
    (frame_w, frame_h), _ = cv2.getTextSize(frame_text, font, font_scale, thickness)
    (fps_w, fps_h), _ = cv2.getTextSize(fps_text, font, font_scale, thickness)
    
    # Calculate total width and height
    padding = 10
    spacing = 8
    total_width = rec_w + spacing + frame_w + spacing + fps_w + (padding * 2)
    total_height = max(rec_h, frame_h, fps_h) + (padding * 2)
    
    # Draw pill background
    annotated_frame = draw_pill_background(
        annotated_frame,
        position[0],
        position[1],
        total_width,
        total_height,
        color=(0, 0, 0),  # Black
        alpha=0.7,
        border_color=(255, 255, 255),  # White border
        border_thickness=1,
    )
    
    # Draw text
    x_offset = position[0] + padding
    y_text = position[1] + padding + rec_h
    
    # REC in red
    cv2.putText(
        annotated_frame,
        rec_text,
        (x_offset, y_text),
        font,
        font_scale,
        (0, 0, 255),  # Red in BGR
        thickness,
        line_type
    )
    
    # FRAME
    x_offset += rec_w + spacing
    cv2.putText(
        annotated_frame,
        frame_text,
        (x_offset, y_text),
        font,
        font_scale,
        (255, 255, 255),  # White in BGR
        thickness,
        line_type
    )
    
    # FPS
    x_offset += frame_w + spacing
    cv2.putText(
        annotated_frame,
        fps_text,
        (x_offset, y_text),
        font,
        font_scale,
        (255, 255, 255),  # White in BGR
        thickness,
        line_type
    )
    
    return annotated_frame


def draw_context_block(
    frame: np.ndarray,
    vlm_result: Dict[str, str],
    object_prompt: str,
    position: Tuple[int, int],
) -> np.ndarray:
    """
    Draw right-aligned context block with VLM metadata.
    
    Args:
        frame: Frame to overlay on (BGR format)
        vlm_result: Dictionary with 'material', 'weight', and 'situation' keys
        object_prompt: Object name/prompt
        position: Top-right position (x, y) - x should be right edge
    
    Returns:
        Frame with context block
    """
    annotated_frame = frame.copy()
    
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 1
    line_type = cv2.LINE_AA
    
    # Get values
    material = vlm_result.get("material", "unknown")
    weight = vlm_result.get("weight", "unknown")
    object_name = object_prompt.upper()
    
    # Text lines
    lines = [
        ("OBJECT", object_name),
        ("MATERIAL", material),
        ("PREDICTED WEIGHT", weight),
    ]
    
    # Calculate text sizes to determine box width
    max_label_width = 0
    max_value_width = 0
    line_height = 20
    padding = 10
    
    for label, value in lines:
        (label_w, label_h), _ = cv2.getTextSize(label, font, font_scale, thickness)
        (value_w, value_h), _ = cv2.getTextSize(value, font, font_scale, thickness)
        max_label_width = max(max_label_width, label_w)
        max_value_width = max(max_value_width, value_w)
    
    # Box dimensions
    box_width = max_label_width + max_value_width + (padding * 3) + 20  # Extra space between label and value
    box_height = len(lines) * line_height + (padding * 2)
    
    # Calculate top-left position (right-aligned)
    x = position[0] - box_width
    y = position[1]
    
    # Draw background box with border
    overlay = annotated_frame.copy()
    cv2.rectangle(
        overlay,
        (x, y),
        (x + box_width, y + box_height),
        (0, 0, 0),  # Black background
        -1
    )
    cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)
    
    # Draw border
    cv2.rectangle(
        annotated_frame,
        (x, y),
        (x + box_width, y + box_height),
        (255, 255, 255),  # White border
        1
    )
    
    # Draw text lines
    y_offset = y + padding + line_height
    for label, value in lines:
        # Draw label in cyan
        cv2.putText(
            annotated_frame,
            label + ":",
            (x + padding, y_offset),
            font,
            font_scale,
            (255, 255, 0),  # Cyan in BGR (#00FFFF)
            thickness,
            line_type
        )
        
        # Draw value in white (right-aligned within box)
        (value_w, value_h), _ = cv2.getTextSize(value, font, font_scale, thickness)
        value_x = x + box_width - padding - value_w
        cv2.putText(
            annotated_frame,
            value,
            (value_x, y_offset),
            font,
            font_scale,
            (255, 255, 255),  # White in BGR
            thickness,
            line_type
        )
        
        y_offset += line_height
    
    return annotated_frame


def extract_action_and_state(situation: str) -> Tuple[str, str]:
    """
    Extract action verb and state from situation description.
    
    Args:
        situation: Situation description from VLM
    
    Returns:
        Tuple of (action_verb, state)
    """
    situation_lower = situation.lower()
    
    # Map common situations to actions and states
    if "open" in situation_lower or "opening" in situation_lower:
        action = "OPENING"
        if "unlatch" in situation_lower or "unlatched" in situation_lower:
            state = "UNLATCHED"
        elif "latch" in situation_lower or "latched" in situation_lower:
            state = "LATCHED"
        else:
            state = "IN PROGRESS"
    elif "pick" in situation_lower or "picking" in situation_lower:
        action = "PICKING"
        state = "IN PROGRESS"
    elif "hold" in situation_lower or "holding" in situation_lower:
        action = "HOLDING"
        state = "HELD"
    elif "lift" in situation_lower or "lifting" in situation_lower:
        action = "LIFTING"
        state = "IN PROGRESS"
    elif "place" in situation_lower or "placing" in situation_lower:
        action = "PLACING"
        state = "IN PROGRESS"
    else:
        # Default: try to extract verb from first word
        words = situation.split()
        if words:
            action = words[0].upper()
        else:
            action = "UNKNOWN"
        state = "UNKNOWN"
    
    return action, state


def draw_action_label(
    frame: np.ndarray,
    mask: Optional[np.ndarray],
    situation: str,
    frame_width: int,
    frame_height: int,
) -> np.ndarray:
    """
    Draw action tag near SAM mask coordinates.
    
    Args:
        frame: Frame to overlay on (BGR format)
        mask: Binary mask for positioning (optional)
        situation: Situation description from VLM
        frame_width: Width of frame (for positioning)
        frame_height: Height of frame (for positioning)
    
    Returns:
        Frame with action label
    """
    annotated_frame = frame.copy()
    
    # Extract action and state
    action, state = extract_action_and_state(situation)
    
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    line_type = cv2.LINE_AA
    
    # Text content
    text = f"ACTION: {action} | STATE: {state}"
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Position ACTION label at top-left (properly aligned)
    padding = 10
    label_x = padding
    label_y = padding + text_height + baseline
    
    # Draw background (dark with border) - semi-transparent
    bg_padding = 5
    overlay = annotated_frame.copy()
    cv2.rectangle(
        overlay,
        (label_x - bg_padding, label_y - text_height - bg_padding),
        (label_x + text_width + bg_padding, label_y + baseline + bg_padding),
        (0, 0, 0),  # Black background
        -1
    )
    # Apply transparency
    cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)
    
    # Draw border
    cv2.rectangle(
        annotated_frame,
        (label_x - bg_padding, label_y - text_height - bg_padding),
        (label_x + text_width + bg_padding, label_y + baseline + bg_padding),
        (255, 255, 255),  # White border
        1
    )
    
    # Draw text in yellow
    cv2.putText(
        annotated_frame,
        text,
        (label_x, label_y),
        font,
        font_scale,
        (0, 255, 255),  # Yellow in BGR (#FFFF00)
        thickness,
        line_type
    )
    
    return annotated_frame


def overlay_vlm_text(frame: np.ndarray, vlm_result: Dict[str, str], position: Tuple[int, int] = (10, 30)) -> np.ndarray:
    """
    Legacy function - kept for backward compatibility.
    Now redirects to new AR HUD overlay system.
    """
    # This function is deprecated but kept for compatibility
    # The new overlay system is called from ProcessVideo
    return frame


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
        # Use GPU 0 if CUDA is available, otherwise use CPU
        if torch.cuda.is_available():
            gpus_to_use = [0]
            print(f"   Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            # For CPU, we need to check SAM 3's requirements
            # Some versions may not support CPU, so we'll try with empty list first
            gpus_to_use = []
        predictor = build_sam3_video_predictor(gpus_to_use=gpus_to_use)
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
    
    # Multi-object detection: detect hands and target object
    print(f"\n4. Detecting hands and target object with SAM 3...")
    max_frames_to_track = max_frames if max_frames else total_frames
    try:
        masks_dict = detect_hands_and_object(
            video_path=video_path,
            object_prompt=text_prompt,
            predictor=predictor,
            max_frames=max_frames_to_track,
        )
        hands_masks = masks_dict["hands"]
        object_masks = masks_dict["object"]
        print(f"   ✓ Multi-object detection complete")
        print(f"      Hands: {len([m for m in hands_masks.values() if m is not None])} frames with detection")
        print(f"      Object: {len([m for m in object_masks.values() if m is not None])} frames with detection")
    except Exception as e:
        print(f"   ✗ Error in multi-object detection: {e}")
        import traceback
        traceback.print_exc()
        cap.release()
        return
    
    # Prepare video writer if output path is specified
    video_writer = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"\n5. Video writer initialized: {output_path}")
    
    # Process frames
    print(f"\n6. Processing frames and displaying results...")
    print("   Press 'q' to quit, 'p' to pause")
    
    # Reset video capture to beginning
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Limit total frames if max_frames is set
    frames_to_process = max_frames_to_track if max_frames else total_frames
    
    frame_count = 0
    last_vlm_result = {"material": "analyzing...", "weight": "analyzing...", "situation": "analyzing..."}
    last_vlm_frame = -vlm_interval  # Force VLM on first frame
    paused = False
    processing_start = time.time()
    vlm_times = []
    
    # Color definitions for visualization
    HAND_COLOR = (255, 255, 0)  # Cyan in BGR
    OBJECT_COLOR = (0, 255, 0)  # Green in BGR
    WIREFRAME_COLOR = (255, 255, 255)  # White in BGR
    
    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret or frame_count >= frames_to_process:
                    break
                
                # Convert BGR to RGB for processing
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Get masks for hands and object
                hand_mask = hands_masks.get(frame_count)
                object_mask = object_masks.get(frame_count)
                
                # Use object mask for VLM analysis (prefer object over hand)
                vlm_mask = object_mask if object_mask is not None else hand_mask
                
                if vlm_mask is not None:
                    # Apply negative masking for VLM
                    masked_frame_rgb = apply_negative_mask(frame_rgb, vlm_mask)
                    
                    # Run VLM every N frames or on first frame
                    if (frame_count - last_vlm_frame) >= vlm_interval:
                        try:
                            vlm_start = time.time()
                            last_vlm_result = vlm_estimator.analyze(masked_frame_rgb)
                            vlm_elapsed = time.time() - vlm_start
                            vlm_times.append(vlm_elapsed)
                            last_vlm_frame = frame_count
                            print(f"   Frame {frame_count}: VLM result - {last_vlm_result} ({vlm_elapsed:.2f}s)")
                        except Exception as e:
                            print(f"   Frame {frame_count}: VLM error (using cached result): {e}")
                
                # Apply color masks for hands and object
                annotated_frame = visualize_multi_object_masks(
                    frame=frame,
                    hand_mask=hand_mask,
                    object_mask=object_mask,
                    hand_color=HAND_COLOR,
                    object_color=OBJECT_COLOR,
                    alpha=0.4,
                    draw_contours=True,
                )
                
                # Add wireframe visualization
                if object_mask is not None:
                    # Draw 2D wireframe for object
                    annotated_frame = draw_wireframe_2d(
                        annotated_frame,
                        object_mask,
                        color=WIREFRAME_COLOR,
                        line_thickness=1,
                        point_skip=5,
                    )
                    # Optional: Draw estimated 3D box
                    # annotated_frame = draw_estimated_3d_box(annotated_frame, object_mask, WIREFRAME_COLOR, 1)
                
                if hand_mask is not None:
                    # Draw 2D wireframe for hands
                    annotated_frame = draw_wireframe_2d(
                        annotated_frame,
                        hand_mask,
                        color=WIREFRAME_COLOR,
                        line_thickness=1,
                        point_skip=5,
                    )
                
                # Draw Professional AR HUD overlays (no system header)
                # 1. Context Block (Top-Right)
                annotated_frame = draw_context_block(
                    annotated_frame,
                    vlm_result=last_vlm_result,
                    object_prompt=text_prompt,
                    position=(width - 10, 10),  # Right edge
                )
                
                # 2. Action Label (Top-Left, properly aligned)
                annotated_frame = draw_action_label(
                    annotated_frame,
                    mask=object_mask if object_mask is not None else hand_mask,
                    situation=last_vlm_result.get("situation", "unknown"),
                    frame_width=width,
                    frame_height=height,
                )
                
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
            print(f"\n7. Output video saved: {output_path}")
        
        if display:
            cv2.destroyAllWindows()
        
        cap.release()
    
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

