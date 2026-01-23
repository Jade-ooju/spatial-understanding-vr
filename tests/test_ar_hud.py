#!/usr/bin/env python3
"""
Test script for the new Professional AR HUD layout.
Tests the overlay system on static images.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
import os


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
    """Draw a semi-transparent pill/capsule-shaped background."""
    annotated_frame = frame.copy()
    overlay = annotated_frame.copy()
    
    radius = height // 2
    
    # Draw filled rounded rectangle (pill shape)
    cv2.rectangle(overlay, (x + radius, y), (x + width - radius, y + height), color, -1)
    cv2.ellipse(overlay, (x + radius, y + radius), (radius, radius), 180, 0, 180, color, -1)
    cv2.ellipse(overlay, (x + width - radius, y + radius), (radius, radius), 0, 0, 180, color, -1)
    
    # Apply transparency
    cv2.addWeighted(overlay, alpha, annotated_frame, 1.0 - alpha, 0, annotated_frame)
    
    # Draw border
    cv2.line(annotated_frame, (x + radius, y), (x + width - radius, y), border_color, border_thickness)
    cv2.line(annotated_frame, (x + radius, y + height), (x + width - radius, y + height), border_color, border_thickness)
    cv2.ellipse(annotated_frame, (x + radius, y + radius), (radius, radius), 180, 0, 180, border_color, border_thickness)
    cv2.ellipse(annotated_frame, (x + width - radius, y + radius), (radius, radius), 0, 0, 180, border_color, border_thickness)
    
    return annotated_frame


def draw_system_header(
    frame: np.ndarray,
    frame_count: int,
    fps: float,
    position: Tuple[int, int] = (10, 10),
) -> np.ndarray:
    """Draw system header with REC indicator, frame count, and FPS."""
    annotated_frame = frame.copy()
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 1
    line_type = cv2.LINE_AA
    
    rec_text = "● REC"
    frame_text = f"FRAME: {frame_count}"
    fps_text = f"FPS: {fps:.1f}"
    
    (rec_w, rec_h), _ = cv2.getTextSize(rec_text, font, font_scale, thickness)
    (frame_w, frame_h), _ = cv2.getTextSize(frame_text, font, font_scale, thickness)
    (fps_w, fps_h), _ = cv2.getTextSize(fps_text, font, font_scale, thickness)
    
    padding = 10
    spacing = 8
    total_width = rec_w + spacing + frame_w + spacing + fps_w + (padding * 2)
    total_height = max(rec_h, frame_h, fps_h) + (padding * 2)
    
    # Draw pill background
    annotated_frame = draw_pill_background(
        annotated_frame, position[0], position[1], total_width, total_height,
        color=(0, 0, 0), alpha=0.7, border_color=(255, 255, 255), border_thickness=1
    )
    
    # Draw text
    x_offset = position[0] + padding
    y_text = position[1] + padding + rec_h
    
    cv2.putText(annotated_frame, rec_text, (x_offset, y_text), font, font_scale, (0, 0, 255), thickness, line_type)
    x_offset += rec_w + spacing
    cv2.putText(annotated_frame, frame_text, (x_offset, y_text), font, font_scale, (255, 255, 255), thickness, line_type)
    x_offset += frame_w + spacing
    cv2.putText(annotated_frame, fps_text, (x_offset, y_text), font, font_scale, (255, 255, 255), thickness, line_type)
    
    return annotated_frame


def draw_context_block(
    frame: np.ndarray,
    vlm_result: Dict[str, str],
    object_prompt: str,
    position: Tuple[int, int],
) -> np.ndarray:
    """Draw right-aligned context block with VLM metadata."""
    annotated_frame = frame.copy()
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 1
    line_type = cv2.LINE_AA
    
    material = vlm_result.get("material", "unknown")
    weight = vlm_result.get("weight", "unknown")
    object_name = object_prompt.upper()
    
    lines = [
        ("OBJECT", object_name),
        ("MATERIAL", material),
        ("PREDICTED WEIGHT", weight),
    ]
    
    max_label_width = 0
    max_value_width = 0
    line_height = 20
    padding = 10
    
    for label, value in lines:
        (label_w, label_h), _ = cv2.getTextSize(label, font, font_scale, thickness)
        (value_w, value_h), _ = cv2.getTextSize(value, font, font_scale, thickness)
        max_label_width = max(max_label_width, label_w)
        max_value_width = max(max_value_width, value_w)
    
    box_width = max_label_width + max_value_width + (padding * 3) + 20
    box_height = len(lines) * line_height + (padding * 2)
    
    x = position[0] - box_width
    y = position[1]
    
    # Draw background
    overlay = annotated_frame.copy()
    cv2.rectangle(overlay, (x, y), (x + box_width, y + box_height), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)
    
    # Draw border
    cv2.rectangle(annotated_frame, (x, y), (x + box_width, y + box_height), (255, 255, 255), 1)
    
    # Draw text
    y_offset = y + padding + line_height
    for label, value in lines:
        cv2.putText(annotated_frame, label + ":", (x + padding, y_offset), font, font_scale, (255, 255, 0), thickness, line_type)
        (value_w, value_h), _ = cv2.getTextSize(value, font, font_scale, thickness)
        value_x = x + box_width - padding - value_w
        cv2.putText(annotated_frame, value, (value_x, y_offset), font, font_scale, (255, 255, 255), thickness, line_type)
        y_offset += line_height
    
    return annotated_frame


def extract_action_and_state(situation: str) -> Tuple[str, str]:
    """Extract action verb and state from situation description."""
    situation_lower = situation.lower()
    
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
        words = situation.split()
        action = words[0].upper() if words else "UNKNOWN"
        state = "UNKNOWN"
    
    return action, state


def draw_action_label(
    frame: np.ndarray,
    mask: Optional[np.ndarray],
    situation: str,
    frame_width: int,
    frame_height: int,
) -> np.ndarray:
    """Draw action tag near SAM mask coordinates."""
    annotated_frame = frame.copy()
    
    action, state = extract_action_and_state(situation)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    line_type = cv2.LINE_AA
    
    text = f"ACTION: {action} | STATE: {state}"
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    padding = 10
    
    # Position ACTION label at top-left (properly aligned)
    label_x = padding
    label_y = padding + text_height + baseline
    
    # Draw background
    bg_padding = 5
    overlay = annotated_frame.copy()
    cv2.rectangle(
        overlay,
        (label_x - bg_padding, label_y - text_height - bg_padding),
        (label_x + text_width + bg_padding, label_y + baseline + bg_padding),
        (0, 0, 0), -1
    )
    cv2.addWeighted(overlay, 0.7, annotated_frame, 0.3, 0, annotated_frame)
    
    # Draw border
    cv2.rectangle(
        annotated_frame,
        (label_x - bg_padding, label_y - text_height - bg_padding),
        (label_x + text_width + bg_padding, label_y + baseline + bg_padding),
        (255, 255, 255), 1
    )
    
    # Draw text in yellow
    cv2.putText(annotated_frame, text, (label_x, label_y), font, font_scale, (0, 255, 255), thickness, line_type)
    
    return annotated_frame


def test_ar_hud_on_image(
    image_path: str,
    output_path: str,
    vlm_result: Dict[str, str],
    object_prompt: str,
    frame_count: int = 0,
    fps: float = 30.0,
    mask: Optional[np.ndarray] = None,
) -> None:
    """Test AR HUD overlay on a single image."""
    print(f"Processing: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return
    
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not load image: {image_path}")
        return
    
    height, width = frame.shape[:2]
    print(f"  Image size: {width}x{height}")
    
    annotated_frame = frame.copy()
    
    # Apply AR HUD overlays (no system header)
    annotated_frame = draw_context_block(annotated_frame, vlm_result, object_prompt, position=(width - 10, 10))
    annotated_frame = draw_action_label(annotated_frame, mask, vlm_result.get("situation", "unknown"), width, height)
    
    cv2.imwrite(output_path, annotated_frame)
    print(f"  Saved: {output_path}")
    print()


def main():
    """Test AR HUD on Door and Waterbottle images."""
    print("=" * 70)
    print("AR HUD Layout Test")
    print("=" * 70)
    print()
    
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test 1: Door image
    print("Test 1: Door Opening Scenario")
    door_vlm_result = {
        "material": "metal/wood",
        "weight": "medium",
        "situation": "opening door handle, unlatching mechanism"
    }
    
    test_ar_hud_on_image(
        image_path="resources/Door.png",
        output_path=os.path.join(output_dir, "door_ar_hud_test.png"),
        vlm_result=door_vlm_result,
        object_prompt="door handle",
        frame_count=40,
        fps=30.0,
        mask=None,
    )
    
    # Test 2: Waterbottle image
    print("Test 2: Water Bottle Opening Scenario")
    bottle_vlm_result = {
        "material": "plastic",
        "weight": "light",
        "situation": "opening water bottle, unscrewing cap"
    }
    
    test_ar_hud_on_image(
        image_path="resources/Waterbottle.png",
        output_path=os.path.join(output_dir, "waterbottle_ar_hud_test.png"),
        vlm_result=bottle_vlm_result,
        object_prompt="water bottle",
        frame_count=60,
        fps=30.0,
        mask=None,
    )
    
    print("=" * 70)
    print("Test Complete!")
    print(f"  Output images saved in: {output_dir}/")
    print("  - door_ar_hud_test.png")
    print("  - waterbottle_ar_hud_test.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
