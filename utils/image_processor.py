from PIL import Image
import os
import shutil
import pathlib
import logging

def sanitize_name(name):
    """Clean filename of invalid characters"""
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()

def process_images(raw_folder_path, processed_folder_path):
    """Process all images in the raw folder and save to processed folder"""
    try:
        # Ensure the processed folder exists
        os.makedirs(processed_folder_path, exist_ok=True)
        
        # Get list of image files
        image_files = [f for f in os.listdir(raw_folder_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            print(f"⚠️ No images found in {raw_folder_path}")
            return
        
        print(f"\nProcessing {len(image_files)} images:")
        print(f"From: {raw_folder_path}")
        print(f"To: {processed_folder_path}")
        
        for idx, filename in enumerate(image_files):
            try:
                input_path = os.path.join(raw_folder_path, filename)
                output_path = os.path.join(processed_folder_path, filename)
                
                print(f"\nProcessing image {idx + 1}/{len(image_files)}: {filename}")
                
                with Image.open(input_path) as img:
                    print(f"Original size: {img.size}")
                    img = img.resize((3600, 3600), Image.LANCZOS)
                    print(f"Resized to: {img.size}")
                    img.save(output_path, dpi=(300, 300))
                    print(f"Saved with 300 DPI to: {output_path}")
            
            except Exception as e:
                print(f"❌ Error processing image {filename}: {e}")
                logging.error(f"Error processing image {filename}: {e}")
                continue
        
        # Verify processed files
        processed_files = [f for f in os.listdir(processed_folder_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        print(f"\n✅ Processed {len(processed_files)}/{len(image_files)} images")
        
    except Exception as e:
        print(f"❌ Error processing folder: {e}")
        logging.error(f"Error processing folder: {e}")
        raise