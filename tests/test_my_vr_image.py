#!/usr/bin/env python3
"""
Quick test script for VR egocentric images with SAM 3
Usage: python tests/test_my_vr_image.py <image_path> [text_prompt]
Example: python tests/test_my_vr_image.py my_vr_image.jpg "hand"

This script uses SAM 3 under the SAM License.
See SAM3_LICENSE in the repository root for license terms.
"""

import sys
import os
import torch
import numpy as np
from PIL import Image
from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor
from sam3.visualization_utils import visualize_formatted_frame_output, prepare_masks_for_visualization
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python tests/test_my_vr_image.py <image_path> [text_prompt]")
        print("Example: python tests/test_my_vr_image.py my_vr_image.jpg 'hand'")
        sys.exit(1)

    image_path = sys.argv[1]
    text_prompt = sys.argv[2] if len(sys.argv) > 2 else "hand"

    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)

    print("=" * 60)
    print("SAM 3 VR Image Segmentation")
    print("=" * 60)
    
    # Load image
    print(f"\n1. Loading image: {image_path}")
    try:
        image = Image.open(image_path).convert("RGB")
        print(f"   ✓ Image loaded: {image.size[0]}x{image.size[1]}")
    except Exception as e:
        print(f"   ✗ Error loading image: {e}")
        sys.exit(1)

    # Load model
    print("\n2. Loading SAM 3 model (this may take a moment)...")
    try:
        device = "cpu"  # Change to "cuda" if you have compatible GPU
        model = build_sam3_image_model(device=device)
        processor = Sam3Processor(model, device=device, confidence_threshold=0.5)
        print("   ✓ Model loaded")
    except Exception as e:
        print(f"   ✗ Error loading model: {e}")
        sys.exit(1)

    # Process image
    print(f"\n3. Segmenting with text prompt: '{text_prompt}'")
    try:
        state = processor.set_image(image)
        state = processor.set_text_prompt(text_prompt, state)
        print(f"   ✓ Segmentation complete")
    except Exception as e:
        print(f"   ✗ Error during segmentation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Display results
    masks = state.get("masks", None)
    scores = state.get("scores", None)
    
    if masks is None or len(masks) == 0:
        print("\n4. Results: No objects found")
        print("   ⚠ No objects found. Try a different prompt or adjust confidence threshold.")
        return
    
    num_objects = len(masks)
    print(f"\n4. Results: Found {num_objects} object(s)")
    
    for i, (mask, score) in enumerate(zip(masks, scores)):
        mask_array = mask.cpu().numpy() if torch.is_tensor(mask) else mask
        mask_pixels = np.sum(mask_array)
        score_val = score.item() if torch.is_tensor(score) else score
        print(f"   Object {i}: score={score_val:.3f}, mask pixels={mask_pixels}")

    # Convert masks to proper format
    obj_id_to_mask = {}
    obj_id_to_score = {}
    for i, (mask, score) in enumerate(zip(masks, scores)):
        # Convert mask to numpy and squeeze any extra dimensions
        mask_array = mask.cpu().numpy() if torch.is_tensor(mask) else mask
        # Handle different mask shapes: (1, H, W) or (H, W)
        if mask_array.ndim == 3:
            mask_array = mask_array.squeeze(0)  # Remove batch dimension if present
        if mask_array.ndim == 3 and mask_array.shape[0] == 1:
            mask_array = mask_array[0]  # Get first channel if (1, H, W)
        # Ensure it's 2D
        if mask_array.ndim != 2:
            mask_array = mask_array.squeeze()
        obj_id_to_mask[i] = mask_array
        obj_id_to_score[i] = score.item() if torch.is_tensor(score) else score
    
    # Create simple visualization
    print("\n5. Creating visualization...")
    try:
        image_array = np.array(image)
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        
        # Original image
        axes[0].imshow(image_array)
        axes[0].set_title("Original Image")
        axes[0].axis("off")
        
        # Overlay masks
        axes[1].imshow(image_array)
        overlay = image_array.copy()
        
        # Color each mask differently
        colors = plt.cm.tab20(np.linspace(0, 1, len(obj_id_to_mask)))
        for obj_id, mask in obj_id_to_mask.items():
            color = colors[obj_id % len(colors)][:3]  # RGB only
            mask_3d = np.stack([mask, mask, mask], axis=-1)
            overlay = np.where(mask_3d, 
                             overlay * 0.5 + np.array(color) * 255 * 0.5, 
                             overlay)
            score = obj_id_to_score[obj_id]
            # Find center of mask for label
            y_coords, x_coords = np.where(mask)
            if len(y_coords) > 0:
                center_y, center_x = int(np.mean(y_coords)), int(np.mean(x_coords))
                axes[1].text(center_x, center_y, f"Obj {obj_id}\n{score:.2f}", 
                           color='white', fontsize=8, ha='center', va='center',
                           bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
        
        axes[1].imshow(overlay.astype(np.uint8))
        axes[1].set_title(f"SAM 3 Segmentation: '{text_prompt}' ({len(obj_id_to_mask)} objects)")
        axes[1].axis("off")
        
        plt.tight_layout()
        # Save to outputs directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, "sam3_result.png")
        plt.savefig(output_filename, dpi=150, bbox_inches="tight")
        print(f"   ✓ Visualization saved to: {output_filename}")
        plt.close()
    except Exception as e:
        print(f"   ⚠ Could not create visualization: {e}")
        import traceback
        traceback.print_exc()

    # Save masks
    print("\n6. Saving individual masks...")
    # Save to outputs directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    for obj_id, mask in obj_id_to_mask.items():
        # Ensure mask is 2D and boolean
        if mask.dtype != bool:
            mask = mask > 0.5
        # Convert to uint8 image
        mask_uint8 = (mask * 255).astype(np.uint8)
        mask_image = Image.fromarray(mask_uint8, mode='L')
        mask_filename = os.path.join(output_dir, f"{base_name}_mask_obj_{obj_id}.png")
        mask_image.save(mask_filename)
        print(f"   ✓ Saved: {mask_filename}")

    print("\n" + "=" * 60)
    print("✓ Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

