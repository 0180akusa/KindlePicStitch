import os
import zipfile
import shutil
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import re
from skimage.metrics._structural_similarity import structural_similarity as ssim

OUTPUT_DIR = r"D:\FFOutput"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class CombinedApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("EPUB and Image Stitching Tool")
        self.geometry("400x600")
        self.resizable(False, False)

        self.create_menu()
        self.create_styles()

        self.epub_frame = EpubFrame(self)
        self.image_stitcher_frame = ImageStitcherFrame(self)

        self.current_frame = None
        self.show_frame("epub")

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        module_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Module", menu=module_menu)
        module_menu.add_command(label="EPUB Processor", command=lambda: self.show_frame("epub"))
        module_menu.add_command(label="Image Stitcher", command=lambda: self.show_frame("image_stitcher"))

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        for btn_num in range(1, 5):
            style.configure(f'ButtonNo{btn_num}.TButton', foreground='#FFFFFF', font=('Helvetica', 12, 'bold'),
                            background='#000000' if btn_num < 4 else '#81001E')
            style.map(f'ButtonNo{btn_num}.TButton', foreground=[('active', '#000000')],
                      background=[('active', '#FFA500')])

    def show_frame(self, frame_name):
        if self.current_frame:
            self.current_frame.pack_forget()

        if frame_name == "epub":
            self.current_frame = self.epub_frame
        elif frame_name == "image_stitcher":
            self.current_frame = self.image_stitcher_frame

        self.current_frame.pack(fill="both", expand=True)

class EpubFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.epub_file = None
        self.reverse_stitch_order = tk.BooleanVar(value=True)
        self.create_widgets()

    def create_widgets(self):
        # Top frame for drop area
        top_frame = ttk.Frame(self, width=400, height=300)
        top_frame.pack_propagate(False)
        top_frame.pack(side=tk.TOP, fill="x")

        # Select EPUB File button
        select_button = ttk.Button(top_frame, text="Select EPUB", style='ButtonNo1.TButton', command=self.select_epub)
        select_button.place(relx=0.5, rely=0.5, anchor='center')

        # Status label
        self.status_label = ttk.Label(self, text="No file imported")
        self.status_label.pack(fill="x", padx=100, pady=10)

        # Process file button
        process_button = ttk.Button(self, text="Process EPUB", style='ButtonNo2.TButton', command=self.process_epub)
        process_button.pack(fill="x", padx=100, pady=10)

        # Reverse stitch checkbox
        reverse_stitch_checkbox = ttk.Checkbutton(self, text="Reverse stitch order", variable=self.reverse_stitch_order)
        reverse_stitch_checkbox.pack(fill="x", padx=100, pady=5)

        # AutoImgStitch button
        auto_img_stitch_button = ttk.Button(self, text="Auto Stitch (Test)", style='ButtonNo3.TButton',
                                            command=self.auto_img_stitch)
        auto_img_stitch_button.pack(fill="x", padx=100, pady=10)

        # PackFolder button
        pack_folder_button = ttk.Button(self, text="Pack to digital", style='ButtonNo4.TButton',
                                        command=self.pack_folder)
        pack_folder_button.pack(fill="x", padx=100, pady=10)

        # Enable drag and drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop)

    def select_epub(self):
        file_path = filedialog.askopenfilename(title="Select an EPUB file", filetypes=[("EPUB files", "*.epub")])
        if file_path:
            self.epub_file = os.path.normpath(file_path)
            self.status_label.config(text=f"Imported file: {os.path.basename(self.epub_file)}")

    def process_epub(self):
        if not self.epub_file:
            messagebox.showerror("Error", "No file imported")
            return

        try:
            zip_file = os.path.splitext(self.epub_file)[0] + '.zip'
            shutil.copy(self.epub_file, zip_file)

            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                images_folders = ['images/'] + [f'{name}images/' for name in file_list if name.endswith('_files/')]

                for images_folder in images_folders:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.startswith(images_folder) and file_info.filename.lower().endswith(
                                ('.jpeg', '.jpg', '.png')):
                            self.process_image(zip_ref, file_info, images_folder)

            os.remove(zip_file)
            self.status_label.config(text="EPUB processed into FFOutput")
        except Exception as e:
            messagebox.showerror("Error", f"Error processing EPUB file: {e}")

    def process_image(self, zip_ref, file_info, images_folder):
        original_filename = file_info.filename.replace(images_folder, '')
        new_filename = original_filename.lstrip('0') or '0'
        new_filename = os.path.splitext(new_filename)[0] + '.jpg'
        new_filepath = os.path.join(OUTPUT_DIR, new_filename)
        os.makedirs(os.path.dirname(new_filepath), exist_ok=True)

        with zip_ref.open(file_info) as source, open(new_filepath, 'wb') as target:
            shutil.copyfileobj(source, target)

        if file_info.filename.lower().endswith('.png'):
            with Image.open(new_filepath) as img:
                rgb_img = img.convert('RGB')
                rgb_img.save(new_filepath, 'JPEG', quality=95)
        elif file_info.filename.lower().endswith('.jpeg'):
            os.rename(new_filepath, new_filepath.replace('.jpeg', '.jpg'))

    def auto_img_stitch(self):
        resolution = self.get_image_resolution(OUTPUT_DIR)
        if resolution is None:
            self.status_label.config(text="No valid images found")
            return

        height, width, channels = resolution
        double_width = width * 2

        stitched_dir = os.path.join(OUTPUT_DIR, "Stitched")
        os.makedirs(stitched_dir, exist_ok=True)

        files = sorted(
            [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(('.jpg', '.png')) and not f.startswith('stitched_')],
            key=lambda x: int(os.path.splitext(x)[0])
        )

        processed_files = set()

        for i in range(0, len(files) - 1, 2):
            if i + 1 >= len(files):
                break

            file_even, file_odd = files[i], files[i + 1]

            if int(os.path.splitext(file_even)[0]) % 2 != 0 or int(os.path.splitext(file_odd)[0]) % 2 != 1:
                continue

            if file_even in processed_files or file_odd in processed_files:
                continue

            img1 = cv2.imread(os.path.join(OUTPUT_DIR, file_even))
            img2 = cv2.imread(os.path.join(OUTPUT_DIR, file_odd))

            if img1.shape == resolution and img2.shape == resolution:
                similarity = self.compare_images(img1, img2)

                if similarity >= 0.75:
                    stitched_image = np.zeros((height, double_width, 3), dtype=np.uint8)
                    if self.reverse_stitch_order.get():
                        stitched_image[:, :width] = img2
                        stitched_image[:, width:] = img1
                    else:
                        stitched_image[:, :width] = img1
                        stitched_image[:, width:] = img2
                    output_filename = os.path.join(OUTPUT_DIR,
                                                   f"{file_even.split('.')[0]}-{file_odd.split('.')[0]}.jpg")
                    cv2.imwrite(output_filename, stitched_image)

                    for file in (file_even, file_odd):
                        shutil.move(os.path.join(OUTPUT_DIR, file), os.path.join(stitched_dir, file))
                        processed_files.add(file)

        self.status_label.config(text="Images Stitched")

    def pack_folder(self):
        target_dir = os.path.join(OUTPUT_DIR, "digital")
        os.makedirs(target_dir, exist_ok=True)

        for item in os.listdir(OUTPUT_DIR):
            source_item = os.path.join(OUTPUT_DIR, item)
            if source_item != target_dir:
                shutil.move(source_item, os.path.join(target_dir, item))

        self.status_label.config(text="All images packed into digital")

    def drop(self, event):
        self.epub_file = os.path.normpath(event.data.strip("{}"))
        self.status_label.config(text=f"Imported file: {os.path.basename(self.epub_file)}")

    def get_image_resolution(self, directory):
        for file in os.listdir(directory):
            if file.lower().endswith(('.jpg', '.png')):
                img = cv2.imread(os.path.join(directory, file))
                if img is not None:
                    return img.shape
        return None

    def compare_images(self, img1, img2):
        edge_sim = self.edge_similarity(img1, img2)
        color_brightness_sim = self.color_brightness_similarity(img1, img2)
        texture_sim = self.texture_similarity(img1, img2)
        pixel_sim = self.pixel_similarity(img1, img2)

        return (edge_sim + color_brightness_sim + texture_sim + pixel_sim) / 4

    def edge_similarity(self, img1, img2):
        edges1 = cv2.Canny(img1, 100, 200)
        edges2 = cv2.Canny(img2, 100, 200)
        return np.mean(edges1 == edges2)

    def color_brightness_similarity(self, img1, img2):
        return 1 - np.mean(cv2.absdiff(img1, img2)) / 255

    def texture_similarity(self, img1, img2):
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        return ssim(gray1, gray2, win_size=7)

    def pixel_similarity(self, img1, img2):
        return ssim(img1, img2, win_size=7, channel_axis=2)

class ImageStitcherFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.image_paths = []
        self.desc_order = tk.BooleanVar(value=True)
        self.max_images = 2
        self.create_widgets()

    def create_widgets(self):
        # Preview area
        self.image_frame = ttk.Frame(self, width=400, height=212)
        self.image_frame.pack(fill="both", pady=(20, 10))
        self.image_frame.pack_propagate(False)

        # Instruction label
        self.instruction_label = ttk.Label(self, text="Drag and drop up to 2 images here", anchor="center")
        self.instruction_label.pack(fill="x", pady=10)

        # Frame for Add Images button and checkbox
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", pady=10)

        # Add Images button
        add_button = ttk.Button(control_frame, text="Add images", style='ButtonNo1.TButton', command=self.add_images)
        add_button.pack(side=tk.LEFT, padx=(100, 10))

        # Checkbox for descending order
        ttk.Checkbutton(control_frame, text="Right to Left", variable=self.desc_order,
                        command=self.reorder_images).pack(side=tk.LEFT)

        # Stitch Images button
        stitch_button = ttk.Button(self, text="Stitch images", style='ButtonNo2.TButton', command=self.stitch_images)
        stitch_button.pack(fill="x", padx=100, pady=10)

        # Pack Images to digital button
        pack_button = ttk.Button(self, text="Pack to digital", style='ButtonNo3.TButton', command=self.pack_FFOutput)
        pack_button.pack(fill="x", padx=100, pady=10)

        # Clear Images button
        clear_button = ttk.Button(self, text="Clean up", style='ButtonNo4.TButton', command=self.clear_images)
        clear_button.pack(fill="x", padx=100, pady=10)

        # Enable drag and drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_images)

    def drop_images(self, event):
        paths = self.tk.splitlist(event.data)
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
        for widget in self.image_frame.winfo_children():
            widget.destroy()

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

        total_images = len(self.image_paths)
        if total_images == 0:
            self.instruction_label.config(text="Drag and drop up to 2 images here")
        elif total_images == 1:
            self.instruction_label.config(text="1 image added. Drag and drop 1 more image here")
        else:
            self.instruction_label.config(text="2 images added. Ready to stitch!")

    def pack_FFOutput(self):
        target_dir = os.path.join(OUTPUT_DIR, "digital")
        os.makedirs(target_dir, exist_ok=True)

        for item in os.listdir(OUTPUT_DIR):
            source_item = os.path.join(OUTPUT_DIR, item)
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
            images = [Image.open(path) for path in self.image_paths]

            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)

            result_image = Image.new('RGB', (total_width, max_height))

            current_width = 0
            for img in images:
                result_image.paste(img, (current_width, 0))
                current_width += img.width

            base_names = [self.extract_number(path) for path in self.image_paths]
            base_names.sort()  # Sort numbers from small to large
            output_filename = f"{'-'.join(map(str, base_names))}.jpg"
            output_dir = os.path.dirname(self.image_paths[0])
            output_path = os.path.join(output_dir, output_filename)

            result_image.save(output_path, quality=95)

            stitched_dir = os.path.join(output_dir, "Stitched")
            os.makedirs(stitched_dir, exist_ok=True)
            for path in self.image_paths:
                shutil.move(path, stitched_dir)

            self.clear_images()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while stitching images: {str(e)}")

if __name__ == "__main__":
    app = CombinedApp()
    app.mainloop()