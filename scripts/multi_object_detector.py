#!/usr/bin/env python3
"""
Multi-Object Detector: Detect hands and target objects separately using SAM 3

This module provides functions to detect both hands and target objects
in videos using separate SAM 3 sessions.

This code is part of the Spatial Understanding for VR project.
"""

import numpy as np
from typing import Dict, Optional, Tuple
import torch


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
    masks = frame_output.get("out_binary_masks", None)
    probs = frame_output.get("out_probs", None)
    
    if masks is None or len(masks) == 0:
        return None
    
    if torch.is_tensor(masks):
        masks = masks.cpu().numpy()
    if isinstance(masks, np.ndarray) and masks.size == 0:
        return None
    
    if probs is not None:
        if torch.is_tensor(probs):
            probs = probs.cpu().numpy()
        if isinstance(probs, np.ndarray) and probs.size == 0:
            probs = None
    
    if probs is not None and len(probs) > 0:
        primary_idx = np.argmax(probs)
    else:
        mask_areas = []
        for mask in masks:
            if torch.is_tensor(mask):
                mask = mask.cpu().numpy()
            mask_areas.append(np.sum(mask))
        if len(mask_areas) == 0:
            return None
        primary_idx = np.argmax(mask_areas)
    
    primary_mask = masks[primary_idx]
    
    if torch.is_tensor(primary_mask):
        primary_mask = primary_mask.cpu().numpy()
    
    if primary_mask.ndim > 2:
        primary_mask = primary_mask.squeeze()
    while primary_mask.ndim > 2:
        primary_mask = primary_mask[0]
    
    if primary_mask.dtype != bool:
        primary_mask = primary_mask > 0.5
    
    return primary_mask


def detect_hands_and_object(
    video_path: str,
    object_prompt: str,
    predictor,
    max_frames: Optional[int] = None,
) -> Dict[str, Dict[int, Optional[np.ndarray]]]:
    """
    Detect both hands and target object in video using separate SAM 3 sessions.
    
    Args:
        video_path: Path to video file
        object_prompt: Text prompt for target object (e.g., "egg", "dumbbell")
        predictor: SAM 3 video predictor instance
        max_frames: Optional limit on number of frames to process
    
    Returns:
        Dictionary with 'hands' and 'object' keys, each containing
        a dict mapping frame_idx to mask (or None if not detected)
    """
    print("=" * 70)
    print("Multi-Object Detection: Hands + Target Object")
    print("=" * 70)
    
    # Get video frame count
    import cv2
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    max_frames_to_track = max_frames if max_frames else total_frames
    
    # Session 1: Detect hands
    print(f"\n1. Detecting hands in video...")
    print(f"   Prompt: 'hand'")
    hands_masks = {}
    
    try:
        response = predictor.handle_request(
            request=dict(
                type="start_session",
                resource_path=video_path,
            )
        )
        session_id_hands = response["session_id"]
        
        # Add prompt for hands
        predictor.handle_request(
            request=dict(
                type="add_prompt",
                session_id=session_id_hands,
                frame_index=0,
                text="hand",
            )
        )
        
        # Propagate through video
        for response in predictor.handle_stream_request(
            request=dict(
                type="propagate_in_video",
                session_id=session_id_hands,
                max_frame_num_to_track=max_frames_to_track,
            )
        ):
            frame_idx = response["frame_index"]
            outputs = response.get("outputs", {})
            mask = extract_primary_mask({frame_idx: outputs}, frame_idx)
            hands_masks[frame_idx] = mask
            
            if (frame_idx + 1) % 50 == 0:
                print(f"   Processed {frame_idx + 1}/{max_frames_to_track} frames...")
        
        detected_count = len([m for m in hands_masks.values() if m is not None])
        print(f"   ✓ Hands detection complete: {len(hands_masks)} frames processed, {detected_count} with detection")
        
        # Close session
        predictor.handle_request(
            request=dict(
                type="close_session",
                session_id=session_id_hands,
            )
        )
    except Exception as e:
        print(f"   ✗ Error detecting hands: {e}")
        import traceback
        traceback.print_exc()
        # Continue with empty hands masks
    
    # Session 2: Detect target object
    print(f"\n2. Detecting target object in video...")
    print(f"   Prompt: '{object_prompt}'")
    object_masks = {}
    
    try:
        response = predictor.handle_request(
            request=dict(
                type="start_session",
                resource_path=video_path,
            )
        )
        session_id_obj = response["session_id"]
        
        # Add prompt for target object
        predictor.handle_request(
            request=dict(
                type="add_prompt",
                session_id=session_id_obj,
                frame_index=0,
                text=object_prompt,
            )
        )
        
        # Propagate through video
        for response in predictor.handle_stream_request(
            request=dict(
                type="propagate_in_video",
                session_id=session_id_obj,
                max_frame_num_to_track=max_frames_to_track,
            )
        ):
            frame_idx = response["frame_index"]
            outputs = response.get("outputs", {})
            # Debug: check if outputs contain masks
            if "out_binary_masks" in outputs:
                num_masks = len(outputs["out_binary_masks"]) if outputs["out_binary_masks"] is not None else 0
                if num_masks > 0 and frame_idx < 5:  # Debug first few frames
                    print(f"   Frame {frame_idx}: Found {num_masks} mask(s)")
            mask = extract_primary_mask({frame_idx: outputs}, frame_idx)
            object_masks[frame_idx] = mask
            
            if (frame_idx + 1) % 50 == 0:
                print(f"   Processed {frame_idx + 1}/{max_frames_to_track} frames...")
        
        detected_count = len([m for m in object_masks.values() if m is not None])
        print(f"   ✓ Object detection complete: {len(object_masks)} frames processed, {detected_count} with detection")
        
        # Close session
        predictor.handle_request(
            request=dict(
                type="close_session",
                session_id=session_id_obj,
            )
        )
    except Exception as e:
        print(f"   ✗ Error detecting object: {e}")
        import traceback
        traceback.print_exc()
        # Continue with empty object masks
    
    print("\n" + "=" * 70)
    print("Multi-Object Detection Complete")
    print("=" * 70)
    
    return {
        "hands": hands_masks,
        "object": object_masks
    }

