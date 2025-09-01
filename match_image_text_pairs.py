#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
import argparse

def match_and_save_pairs(image_folder, text_folder, output_folder, max_pairs=None):
    """
    Find matching image and text files based on filename and copy pairs to output folder
    
    Args:
        image_folder: Path to folder containing images
        text_folder: Path to folder containing text files
        output_folder: Path to output folder for matched pairs
        max_pairs: Maximum number of pairs to copy (None for all)
    """
    image_folder = Path(image_folder)
    text_folder = Path(text_folder)
    output_folder = Path(output_folder)
    
    # Create output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Common image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    # Find all image files
    image_files = {}
    for img_file in image_folder.iterdir():
        if img_file.is_file() and img_file.suffix.lower() in image_extensions:
            base_name = img_file.stem
            image_files[base_name] = img_file
    
    # Find matching text files and copy pairs
    matched_pairs = 0
    unmatched_images = []
    
    for base_name, img_file in image_files.items():
        # Stop if we've reached the maximum number of pairs
        if max_pairs is not None and matched_pairs >= max_pairs:
            break
            
        # Look for corresponding text file
        txt_file = text_folder / f"{base_name}.txt"
        
        if txt_file.exists():
            # Copy both files to output folder
            shutil.copy2(img_file, output_folder / img_file.name)
            shutil.copy2(txt_file, output_folder / txt_file.name)
            matched_pairs += 1
            print(f"Matched: {img_file.name} <-> {txt_file.name}")
        else:
            unmatched_images.append(img_file.name)
    
    print(f"\nSummary:")
    print(f"Total images found: {len(image_files)}")
    print(f"Matched pairs: {matched_pairs}")
    print(f"Unmatched images: {len(unmatched_images)}")
    
    if unmatched_images:
        print(f"\nUnmatched image files:")
        for img in unmatched_images[:10]:  # Show first 10
            print(f"  - {img}")
        if len(unmatched_images) > 10:
            print(f"  ... and {len(unmatched_images) - 10} more")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Match image files with corresponding text files")
    parser.add_argument("image_folder", help="Path to folder containing images")
    parser.add_argument("text_folder", help="Path to folder containing text files")
    parser.add_argument("output_folder", help="Path to output folder for matched pairs")
    parser.add_argument("size", type=int, help="data size")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_folder):
        print(f"Error: Image folder '{args.image_folder}' does not exist")
        exit(1)
    
    if not os.path.exists(args.text_folder):
        print(f"Error: Text folder '{args.text_folder}' does not exist")
        exit(1)
    
    match_and_save_pairs(args.image_folder, args.text_folder, args.output_folder, args.size)
