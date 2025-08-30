#!/usr/bin/env python3
"""
Prepare training dataset by copying paired image and text files.

Usage:
    python prepare_dataset.py --output_dir /path/to/training_data \
                             --image_dir /path/to/images \
                             --text_dir /path/to/texts
    
    # If images and texts are in same directory:
    python prepare_dataset.py --output_dir /path/to/training_data \
                             --image_dir /path/to/data \
                             --text_dir /path/to/data
"""

import argparse
import shutil
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description='Prepare training dataset by copying paired image and text files')
    parser.add_argument('--output_dir', '-o', required=True, help='Output directory for training data')
    parser.add_argument('--image_dir', '-i', required=True, help='Directory containing images')  
    parser.add_argument('--text_dir', '-t', required=True, help='Directory containing text files')
    parser.add_argument('--symlink', action='store_true', help='Create symlinks instead of copying (saves space)')
    parser.add_argument('--extensions', default='jpg,jpeg,png,webp,bmp,tiff', 
                       help='Comma-separated list of image extensions to process')
    parser.add_argument('--dry_run', action='store_true', help='Show what would be copied without actually copying')
    
    args = parser.parse_args()
    
    # Setup paths
    output_dir = Path(args.output_dir).resolve()
    image_dir = Path(args.image_dir).resolve()
    text_dir = Path(args.text_dir).resolve()
    
    # Validate inputs
    if not image_dir.exists():
        print(f"Error: Image directory {image_dir} does not exist")
        sys.exit(1)
        
    if not text_dir.exists():
        print(f"Error: Text directory {text_dir} does not exist")
        sys.exit(1)
    
    # Parse extensions
    extensions = [f'.{ext.strip().lower()}' for ext in args.extensions.split(',')]
    
    print(f"Image directory: {image_dir}")
    print(f"Text directory: {text_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Looking for extensions: {extensions}")
    print(f"Operation: {'symlink' if args.symlink else 'copy'}")
    
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find and process image files
    copied_count = 0
    missing_text_count = 0
    
    for img_path in image_dir.iterdir():
        if not img_path.is_file() or img_path.suffix.lower() not in extensions:
            continue
            
        base_name = img_path.stem
        text_path = text_dir / f"{base_name}.txt"
        
        # Check if corresponding text file exists
        if not text_path.exists():
            print(f"Warning: No text file found for {img_path.name}")
            missing_text_count += 1
            continue
        
        if args.dry_run:
            print(f"Would copy: {img_path.name} + {text_path.name}")
        else:
            # Copy or symlink files
            if args.symlink:
                (output_dir / img_path.name).symlink_to(img_path)
                (output_dir / text_path.name).symlink_to(text_path)
            else:
                shutil.copy2(img_path, output_dir / img_path.name)
                shutil.copy2(text_path, output_dir / text_path.name)
            
            print(f"Processed: {img_path.name} + {text_path.name}")
        
        copied_count += 1
    
    print(f"\nSummary:")
    print(f"  Processed pairs: {copied_count}")
    print(f"  Missing text files: {missing_text_count}")
    
    if not args.dry_run and copied_count > 0:
        print(f"\nDataset ready at: {output_dir}")
        print(f"\nTo train, update your dataset.toml with:")
        print(f"[[directory]]")
        print(f"path = '{output_dir}'")
        print(f"num_repeats = 1")


if __name__ == '__main__':
    main()