import os
import shutil
import csv
from PIL import Image
import numpy as np

def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

def compare_edges(img1, img2, edge_width=5, threshold=500):
    img1_gray = img1.convert('L')
    img2_gray = img2.convert('L')

    edge1 = np.array(img1_gray)[:, :edge_width]
    edge2 = np.array(img2_gray)[:, -edge_width:]

    print(f"Edge 1 shape: {edge1.shape}, Edge 2 shape: {edge2.shape}")

    min_height = min(edge1.shape[0], edge2.shape[0])
    edge1 = edge1[:min_height]
    edge2 = edge2[:min_height]

    print(f"Adjusted edge shapes: {edge1.shape}, {edge2.shape}")

    error = mse(edge1, edge2)

    print(f"MSE between edges: {error}")
    print(f"Threshold: {threshold}")

    return error, error < threshold

def join_images(img1, img2):
    if img1.size[1] != img2.size[1]:
        min_height = min(img1.size[1], img2.size[1])
        img1 = img1.crop((0, 0, img1.size[0], min_height))
        img2 = img2.crop((0, 0, img2.size[0], min_height))

    joined_image = Image.new('RGB', (img1.size[0] + img2.size[0], img1.size[1]))

    joined_image.paste(img2, (0, 0))
    joined_image.paste(img1, (img2.size[0], 0))

    return joined_image

def process_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    images = sorted([f for f in os.listdir(input_dir) if f.endswith('.jpg') and f[:-4].isdigit()],
                    key=lambda x: int(x[:-4]))

    print(f"Found {len(images)} images to process")

    # Create CSV file for results
    csv_path = os.path.join(input_dir, 'comparison_results.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Image 1', 'Image 2', 'Similarity Score'])

        for i in range(0, len(images) - 1, 2):
            if i + 1 >= len(images):
                print(f"No pair for {images[i]}, processing complete.")
                break

            img1_path = os.path.join(input_dir, images[i])
            img2_path = os.path.join(input_dir, images[i + 1])

            print(f"\nComparing images: {images[i]} and {images[i + 1]}")

            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)

            print(f"Image 1 size: {img1.size}, Image 2 size: {img2.size}")

            error, is_match = compare_edges(img1, img2)
            
            # Write comparison result to CSV
            csvwriter.writerow([images[i], images[i + 1], error])

            if is_match:
                new_filename = f"{images[i][:-4]}-{images[i + 1][:-4]}.jpg"
                print(f"Match found: {new_filename}")

                joined_image = join_images(img1, img2)

                joined_image_path = os.path.join(input_dir, new_filename)
                joined_image.save(joined_image_path)
                print(f"Saved joined image: {joined_image_path}")

                # Move original images to Stitched folder
                shutil.move(img1_path, os.path.join(output_dir, images[i]))
                shutil.move(img2_path, os.path.join(output_dir, images[i + 1]))
                print(f"Moved {images[i]} and {images[i + 1]} to {output_dir}")
            else:
                print("No match found")

    print(f"Comparison results saved to {csv_path}")

if __name__ == "__main__":
    input_directory = r"D:\FFOutput"
    output_directory = r"D:\FFOutput\Stitched"
    print(f"Processing images from {input_directory}")
    print(f"Output directory: {output_directory}")
    process_images(input_directory, output_directory)
    print("Processing complete")