#!/usr/bin/env python3
"""
Debug script to test face verification locally.
Usage:
    python debug_verify.py --ref reference.jpg --current current.jpg [--threshold 0.65]
    python debug_verify.py --base64 --ref ref_b64.txt --current curr_b64.txt [--threshold 0.65]

This helps diagnose why face verification might be failing.
"""

import sys
import argparse
import base64
import cv2
import numpy as np
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from face_verifier import FaceVerifier


def image_to_base64(image_path: str) -> str:
    """Convert an image file to base64 string"""
    with open(image_path, 'rb') as f:
        data = f.read()
    return f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"


def test_verification(ref_path: str, curr_path: str, threshold: float = 0.65):
    """Test face verification between two images"""
    print(f"\n{'='*60}")
    print(f"FACE VERIFICATION DEBUG TEST")
    print(f"{'='*60}")
    print(f"Threshold: {threshold}")
    print(f"Reference: {ref_path}")
    print(f"Current:   {curr_path}")
    print(f"{'='*60}\n")
    
    # Create verifier
    verifier = FaceVerifier(threshold=threshold)
    
    # Check if inputs are base64 files or image paths
    if ref_path.endswith('.txt'):
        with open(ref_path, 'r') as f:
            ref_b64 = f.read().strip()
    else:
        ref_b64 = image_to_base64(ref_path)
    
    if curr_path.endswith('.txt'):
        with open(curr_path, 'r') as f:
            curr_b64 = f.read().strip()
    else:
        curr_b64 = image_to_base64(curr_path)
    
    # Decode and check images
    ref_img = verifier.decode_base64_image(ref_b64)
    curr_img = verifier.decode_base64_image(curr_b64)
    
    if ref_img is None:
        print("ERROR: Could not decode reference image!")
        return
    if curr_img is None:
        print("ERROR: Could not decode current image!")
        return
    
    print(f"Reference image size: {ref_img.shape}")
    print(f"Current image size:   {curr_img.shape}")
    print()
    
    # Get face signatures separately for debugging
    print("Extracting reference face signature...")
    ref_sig = verifier.get_face_signature(ref_img)
    if ref_sig is None:
        print("ERROR: No face detected in reference image!")
        print("Tips:")
        print("  - Ensure face is clearly visible")
        print("  - Use good lighting")
        print("  - Face should be front-facing")
        return
    print(f"Reference signature: {ref_sig[:5]}... (len={len(ref_sig)})")
    print()
    
    print("Extracting current face signature...")
    curr_sig = verifier.get_face_signature(curr_img)
    if curr_sig is None:
        print("ERROR: No face detected in current image!")
        print("Tips:")
        print("  - Ensure face is clearly visible")
        print("  - Use good lighting")
        print("  - Face should be front-facing")
        return
    print(f"Current signature:   {curr_sig[:5]}... (len={len(curr_sig)})")
    print()
    
    # Compute similarity
    print("Computing similarity...")
    similarity, distance = verifier.compute_similarity(ref_sig, curr_sig)
    print(f"\nSimilarity:  {similarity:.4f}")
    print(f"Distance:    {distance:.4f}")
    print(f"Threshold:   {threshold}")
    print(f"Result:      {'MATCH ✓' if similarity >= threshold else 'NO MATCH ✗'}")
    print()
    
    # Full verification
    print("Running full verification...")
    is_match, confidence, debug_info = verifier.verify(ref_b64, curr_img)
    print(f"\nFull Verification Result:")
    print(f"  is_match:    {is_match}")
    print(f"  confidence:  {confidence:.4f}")
    print(f"  debug_info:  {debug_info}")
    print()
    
    # Test with different thresholds
    print("Testing different thresholds:")
    for t in [0.45, 0.55, 0.65, 0.75, 0.85]:
        v = FaceVerifier(threshold=t)
        match, conf, _ = v.verify(ref_b64, curr_img)
        status = "MATCH" if match else "NO MATCH"
        print(f"  threshold={t:.2f} -> {status} (confidence={conf:.4f})")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}\n")


def test_same_image(image_path: str, threshold: float = 0.65):
    """Test verification of an image against itself (should always match)"""
    print(f"\nTesting same-image verification with: {image_path}")
    test_verification(image_path, image_path, threshold)


def main():
    parser = argparse.ArgumentParser(description='Debug face verification')
    parser.add_argument('--ref', '-r', required=True, help='Reference image path or base64 text file')
    parser.add_argument('--current', '-c', required=True, help='Current image path or base64 text file')
    parser.add_argument('--threshold', '-t', type=float, default=0.65, help='Verification threshold (default: 0.65)')
    parser.add_argument('--same', '-s', help='Test with same image (shortcut)')
    
    args = parser.parse_args()
    
    if args.same:
        test_same_image(args.same, args.threshold)
    else:
        test_verification(args.ref, args.current, args.threshold)


if __name__ == '__main__':
    main()

