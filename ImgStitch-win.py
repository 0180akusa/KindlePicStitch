import argparse
from PIL import Image
import os
import shutil
import sys

def extract_number(filename):
    return int(''.join(filter(str.isdigit, filename)))

def stitch_images(image_paths, right_to_left):
    try:
        # Open images
        images = [Image.open(path) for path in image_paths]

        # Determine the size of the stitched image
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        # Create a new image with the total width and max height
        result_image = Image.new('RGB', (total_width, max_height))

        # Paste the images side by side
        current_width = 0
        for img in (reversed(images) if right_to_left else images):
            result_image.paste(img, (current_width, 0))
            current_width += img.width

        return result_image
    except Exception as e:
        print(f"An error occurred while stitching images: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Stitch two images together.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-r", action="store_true", help="Stitch images from right to left")
    group.add_argument("-l", action="store_true", help="Stitch images from left to right")
    parser.add_argument("image1", help="Path to the first image")
    parser.add_argument("image2", help="Path to the second image")
    args = parser.parse_args()

    if not (args.image1.lower().endswith('.jpg') and args.image2.lower().endswith('.jpg')):
        print("请选择2张jpg图片。")
        sys.exit(1)

    image_paths = [args.image1, args.image2]
    right_to_left = args.r

    # Stitch images
    result_image = stitch_images(image_paths, right_to_left)

    # Generate output filename
    base_names = [extract_number(os.path.basename(path)) for path in image_paths]
    base_names.sort()
    output_filename = f"{'-'.join(map(str, base_names))}.jpg"
    output_dir = os.path.dirname(image_paths[0])
    output_path = os.path.join(output_dir, output_filename)

    # Save stitched image
    result_image.save(output_path, quality=95)

    # Move the original images to the "Stitched" folder
    stitched_dir = os.path.join(output_dir, "Stitched")
    os.makedirs(stitched_dir, exist_ok=True)
    for path in image_paths:
        shutil.move(path, stitched_dir)

    print(f"Stitched image saved to {output_path}")
    print(f"Original images moved to {stitched_dir}")

if __name__ == "__main__":
    main()