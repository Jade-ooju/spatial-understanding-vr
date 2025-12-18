#!/usr/bin/env python3
"""
Crop video to a shorter segment for testing and memory optimization.
"""

import argparse
import cv2
import os
import sys

def crop_video(input_path: str, output_path: str, start_frame: int = 0, num_frames: int = 100, fps: float = None):
    """
    Crop video to extract a segment.
    
    Args:
        input_path: Input video path
        output_path: Output video path
        start_frame: Starting frame number (0-indexed)
        num_frames: Number of frames to extract
        fps: Output FPS (uses input FPS if None)
    """
    if not os.path.exists(input_path):
        print(f"Error: Input video not found: {input_path}")
        sys.exit(1)
    
    print(f"Opening video: {input_path}")
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video: {input_path}")
        sys.exit(1)
    
    # Get video properties
    input_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Input video: {width}x{height} @ {input_fps} FPS, {total_frames} frames")
    
    # Use input FPS if not specified
    if fps is None:
        fps = input_fps
    
    # Check bounds
    if start_frame >= total_frames:
        print(f"Error: Start frame {start_frame} exceeds total frames {total_frames}")
        sys.exit(1)
    
    if start_frame + num_frames > total_frames:
        num_frames = total_frames - start_frame
        print(f"Warning: Adjusted to {num_frames} frames (end of video)")
    
    # Seek to start frame
    print(f"Seeking to frame {start_frame}...")
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print(f"Error: Could not create output video: {output_path}")
        sys.exit(1)
    
    print(f"Extracting {num_frames} frames starting from frame {start_frame}...")
    print(f"Output: {output_path} ({width}x{height} @ {fps} FPS)")
    
    frames_written = 0
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            print(f"Warning: Could not read frame {start_frame + i}")
            break
        
        out.write(frame)
        frames_written += 1
        
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{num_frames} frames ({100 * (i + 1) / num_frames:.1f}%)")
    
    cap.release()
    out.release()
    
    print(f"\n✓ Successfully cropped video!")
    print(f"  Input: {input_path} ({total_frames} frames)")
    print(f"  Output: {output_path} ({frames_written} frames)")
    print(f"  Extracted: frames {start_frame} to {start_frame + frames_written - 1}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crop video to shorter segment")
    parser.add_argument("--input", "-i", required=True, help="Input video path")
    parser.add_argument("--output", "-o", required=True, help="Output video path")
    parser.add_argument("--start", "-s", type=int, default=0, help="Starting frame (default: 0)")
    parser.add_argument("--frames", "-f", type=int, default=100, help="Number of frames to extract (default: 100)")
    parser.add_argument("--fps", type=float, default=None, help="Output FPS (uses input FPS if not specified)")
    
    args = parser.parse_args()
    
    crop_video(args.input, args.output, args.start, args.frames, args.fps)






