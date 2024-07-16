import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import os
import re
import shutil

foutput_dir = r"D:\FFOutput"

class ImageStitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Stitcher")
        
        # Set window size with 2:3 aspect ratio
        window_width = 400
        window_height = 600
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(False, False)  # Disable window resizing

        # Initialize DnD (Drag and Drop)
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_images)

        # Variables for image stitching
        self.image_paths = []
        self.desc_order = tk.BooleanVar(value=True)  # Default to left large, right small
        self.max_images = 2  # Limit to 2 images

        # Create UI elements
        self.create_widgets(window_width, window_height)

    def create_widgets(self, width, height):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Preview area (17:9 aspect ratio)
        preview_height = int(width * 9 / 17)
        self.image_frame = ttk.Frame(main_frame, width=width, height=preview_height)
        self.image_frame.pack(fill="both", pady=(20, 10))
        self.image_frame.pack_propagate(False)

        # Instruction label
        self.instruction_label = ttk.Label(main_frame, text="Drag and drop up to 2 images here", anchor="center")
        self.instruction_label.pack(fill="x", pady=10)

        # Styple for Button
        style = ttk.Style()
        style.theme_use('clam')

        # Styple for ButtonNo1
        style.configure('ButtonNo1.TButton',foreground='#FFFFFF', font=('Helvetica', 12, 'bold'), background='#000000')
        style.map('ButtonNo1.TButton', foreground=[('active','#000000')], background=[('active','#FFA500')])

        # Styple for ButtonNo2
        style.configure('ButtonNo2.TButton',foreground='#FFFFFF', font=('Helvetica', 12, 'bold'), background='#000000')
        style.map('ButtonNo2.TButton', foreground=[('active','#000000')], background=[('active','#FFA500')])

        # Styple for ButtonNo3
        style.configure('ButtonNo3.TButton',foreground='#FFFFFF', font=('Helvetica', 12, 'bold'), background='#000000')
        style.map('ButtonNo3.TButton', foreground=[('active','#000000')], background=[('active','#FFA500')])

        # Styple for ButtonNo4
        style.configure('ButtonNo4.TButton',foreground='#FFFFFF', font=('Helvetica', 12, 'bold'), background='#81001E')
        style.map('ButtonNo4.TButton', foreground=[('active','#000000')], background=[('active','#FFA500')])

        # Frame for Add Images button and checkbox
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=10)

        # Add Images button
        add_button = ttk.Button(control_frame, text="Add images", style='ButtonNo1.TButton', command=self.add_images)
        add_button.pack(side=tk.LEFT, padx=(width//4, 10))

        # Checkbox for descending order
        ttk.Checkbutton(control_frame, text="Right to Left", variable=self.desc_order, command=self.reorder_images).pack(side=tk.LEFT)

        # Stitch Images button
        stitch_button = ttk.Button(main_frame, text="Stitch images", style='ButtonNo2.TButton', command=self.stitch_images)
        stitch_button.pack(fill="x", padx=width//4, pady=10)

        # Pack Images to digital button
        stitch_button = ttk.Button(main_frame, text="Pack to digital", style='ButtonNo3.TButton', command=self.pack_FFOutput)
        stitch_button.pack(fill="x", padx=width//4, pady=10)

        # Clear Images button
        clear_button = ttk.Button(main_frame, text="Clean up", style='ButtonNo4.TButton', command=self.clear_images)
        clear_button.pack(fill="x", padx=width//4, pady=10)

    def drop_images(self, event):
        paths = self.root.tk.splitlist(event.data)
        self.process_new_images(paths)

    def add_images(self):
        paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        self.process_new_images(paths)

    def process_new_images(self, paths):
        remaining_slots = self.max_images - len(self.image_paths)
        if remaining_slots > 0:
            new_paths = paths[:remaining_slots]
            self.image_paths.extend(new_paths)
            self.reorder_images()
            if len(paths) > remaining_slots:
                messagebox.showinfo("Image Limit Reached", f"Only added {remaining_slots} image(s). The maximum of 2 images has been reached.")
        else:
            messagebox.showinfo("Image Limit Reached", "Cannot add more images. The maximum of 2 images has been reached.")

    def extract_number(self, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        number = re.sub(r'^0+', '', filename)  # Remove leading zeros
        return int(number) if number.isdigit() else filename

    def reorder_images(self):
        if len(self.image_paths) == 2:
            numbers = [self.extract_number(path) for path in self.image_paths]
            if self.desc_order.get():
                self.image_paths.sort(key=self.extract_number, reverse=True)
            else:
                self.image_paths.sort(key=self.extract_number)
        self.show_images()

    def show_images(self):
        # Clear previous images
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        # Display images
        for i, path in enumerate(self.image_paths):
            try:
                img = Image.open(path)
                img.thumbnail((self.image_frame.winfo_width()//2 - 20, self.image_frame.winfo_height() - 20))
                img = ImageTk.PhotoImage(img)
                label = ttk.Label(self.image_frame, image=img)
                label.image = img  # Keep reference to image
                label.pack(side=tk.LEFT, padx=10)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image {path}: {str(e)}")

        # Update the instruction label
        total_images = len(self.image_paths)
        if total_images == 0:
            self.instruction_label.config(text="Drag and drop up to 2 images here")
        elif total_images == 1:
            self.instruction_label.config(text="1 image added. Drag and drop 1 more image here")
        else:
            self.instruction_label.config(text="2 images added. Ready to stitch!")
    
    def pack_FFOutput(self):
        global foutput_dir
        target_dir = os.path.join(foutput_dir, "digital")
        os.makedirs(target_dir, exist_ok=True)

        # Move all items except the target directory itself
        for item in os.listdir(foutput_dir):
            source_item = os.path.join(foutput_dir, item)
            target_item = os.path.join(target_dir, item)

            if os.path.isdir(source_item) and source_item != target_dir:
                shutil.move(source_item, target_item)
            elif os.path.isfile(source_item):
                shutil.move(source_item, target_item)

        messagebox.showinfo("Completed", f"All files have been moved to {target_dir}")

    def clear_images(self):
        self.image_paths = []
        self.show_images()

    def stitch_images(self):
        if len(self.image_paths) != 2:
            messagebox.showerror("Error", "Please add exactly 2 images before stitching.")
            return

        try:
            # Open images
            images = [Image.open(path) for path in self.image_paths]

            # Determine the size of the stitched image
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)

            # Create a new image with the total width and max height
            result_image = Image.new('RGB', (total_width, max_height))

            # Paste the images side by side
            current_width = 0
            for img in images:
                result_image.paste(img, (current_width, 0))
                current_width += img.width

            # Get output filename (always small-large.jpg)
            base_names = [self.extract_number(path) for path in self.image_paths]
            base_names.sort()  # Sort numbers from small to large
            output_filename = f"{'-'.join(map(str, base_names))}.jpg"
            output_dir = os.path.dirname(self.image_paths[0])
            output_path = os.path.join(output_dir, output_filename)

            # Save stitched image
            result_image.save(output_path, quality=95)

            # Move the original images to the "Stitched" folder
            stitched_dir = os.path.join(output_dir, "Stitched")
            os.makedirs(stitched_dir, exist_ok=True)
            for path in self.image_paths:
                shutil.move(path, stitched_dir)

            # Clear images after saving
            self.clear_images()

            # messagebox.showinfo("Success", f"Stitched image saved to {output_path}\nOriginal images moved to {stitched_dir}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while stitching images: {str(e)}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ImageStitcherApp(root)
    root.mainloop()
