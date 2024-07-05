import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import os
import re

class ImageStitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Stitcher")

        # Initialize DnD (Drag and Drop)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_images)

        # Variables for image stitching
        self.image_paths = []
        self.rows = tk.IntVar(value=1)
        self.cols = tk.IntVar(value=2)
        self.desc_order = tk.BooleanVar(value=True)  # Default to left large, right small

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Frame for images display
        self.image_frame = tk.Frame(self.root)
        self.image_frame.grid(row=0, column=0, columnspan=4, pady=10)

        # Label for drag and drop area
        self.drop_area = tk.Label(self.root, text="Drag and drop images here", relief="solid", width=40, height=10)
        self.drop_area.grid(row=1, column=0, columnspan=4, pady=10)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.drop_images)

        # Button to add images
        add_button = tk.Button(self.root, text="Add Images", command=self.add_images)
        add_button.grid(row=2, column=0, pady=5)

        # Entry for rows
        row_label = tk.Label(self.root, text="Rows:")
        row_label.grid(row=2, column=1)
        row_entry = tk.Entry(self.root, textvariable=self.rows)
        row_entry.grid(row=2, column=2)

        # Entry for columns
        col_label = tk.Label(self.root, text="Columns:")
        col_label.grid(row=3, column=1)
        col_entry = tk.Entry(self.root, textvariable=self.cols)
        col_entry.grid(row=3, column=2)

        # Checkbox for descending order
        desc_checkbox = tk.Checkbutton(self.root, text="Desc", variable=self.desc_order)
        desc_checkbox.grid(row=4, column=0, columnspan=4, pady=5)

        # Button to stitch images
        stitch_button = tk.Button(self.root, text="Stitch Images", command=self.stitch_images)
        stitch_button.grid(row=5, column=0, columnspan=4, pady=10)

        # Button to clear images
        clear_button = tk.Button(self.root, text="Clear Images", command=self.clear_images)
        clear_button.grid(row=6, column=0, columnspan=4, pady=10)

    def drop_images(self, event):
        paths = self.root.tk.splitlist(event.data)
        order = self.desc_order.get()
        self.image_paths.extend(sorted(paths, key=self.extract_number, reverse=order))
        self.show_images()

    def add_images(self):
        paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if paths:
            order = self.desc_order.get()
            self.image_paths.extend(sorted(paths, key=self.extract_number, reverse=order))
            self.show_images()

    def extract_number(self, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        number = re.sub(r'^0+', '', filename)  # Remove leading zeros
        return int(number) if number.isdigit() else filename

    def show_images(self):
        # Clear previous images
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        # Display images in the frame
        for path in self.image_paths:
            try:
                img = Image.open(path)
                img.thumbnail((150, 150))  # Resize image for display
                img = ImageTk.PhotoImage(img)
                label = tk.Label(self.image_frame, image=img)
                label.image = img  # Keep reference to image
                label.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image {path}: {str(e)}")

    def clear_images(self):
        self.image_paths = []
        self.show_images()

    def stitch_images(self):
        try:
            rows = self.rows.get()
            cols = self.cols.get()

            if rows <= 0 or cols <= 0:
                messagebox.showerror("Error", "Rows and Columns must be greater than zero.")
                return

            if len(self.image_paths) < rows * cols:
                messagebox.showerror("Error", "Not enough images to fill the grid.")
                return

            # Open all images
            images = [Image.open(path) for path in self.image_paths]

            # Assuming all images have the same dimensions
            width, height = images[0].size

            # Create a new image for stitching
            result_width = width * cols
            result_height = height * rows
            result_image = Image.new('RGB', (result_width, result_height))

            # Stitch images
            for row in range(rows):
                for col in range(cols):
                    index = row * cols + col
                    if index < len(images):
                        result_image.paste(images[index], (col * width, row * height))

            # Get directory and base filenames
            base_names = [os.path.splitext(os.path.basename(path))[0] for path in self.image_paths[:rows * cols]]
            base_numbers = [re.sub(r'^0+', '', name) for name in base_names]
            output_filename = "-".join(sorted(base_numbers)) + ".jpg"  # Sort numbers for the output filename
            output_dir = os.path.dirname(self.image_paths[0])
            output_path = os.path.join(output_dir, output_filename)

            # Save stitched image
            result_image.save(output_path, quality=95)  # Set quality to 95 to reduce compression artifacts

            # Clear images after saving, but retain rows, cols, and desc_order states
            self.clear_images()

            # Remove the drag and drop area
            self.drop_area.grid_remove()

            # Restore drag and drop area
            self.drop_area.grid(row=1, column=0, columnspan=4, pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            # Close all images
            for image in images:
                image.close()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ImageStitcherApp(root)
    root.mainloop()
