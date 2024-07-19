import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import os, zipfile, shutil, cv2, numpy as np, re
from skimage.metrics._structural_similarity import structural_similarity as ssim

OUTPUT_DIR = r"D:\FFOutput"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class OptimizedApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("EPUB to JPG Stitch Tool")
        self.geometry("400x600")  # 增加窗口高度
        self.resizable(False, False)

        self.create_styles()
        self.combined_frame = CombinedFrame(self)
        self.combined_frame.pack(fill="both", expand=True)

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        for btn_num in range(1, 5):
            style.configure(f'ButtonNo{btn_num}.TButton', foreground='#FFFFFF', font=('Helvetica', 12, 'bold'),
                            background='#000000' if btn_num < 4 else '#81001E')
            style.map(f'ButtonNo{btn_num}.TButton', foreground=[('active', '#000000')],
                      background=[('active', '#FFA500')])
        
        # 添加新的样式用于拖放区域
        style.configure('DropZone.TFrame', background='#E0E0E0', relief='groove', borderwidth=2)

class CombinedFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.epub_file = None
        self.image_paths = []
        self.desc_order = tk.BooleanVar(value=True)
        self.max_images = 2
        self.initial_epub_text = "Import EPUB here"
        self.initial_image_text = "Import jpg here (max 2)"
        self.create_widgets()

    def create_widgets(self):
        # EPUB导入区域（上方）
        self.epub_frame = ttk.Frame(self, width=380, height=100, style='DropZone.TFrame')
        self.epub_frame.pack(pady=(10, 5), padx=10)
        self.epub_frame.pack_propagate(False)

        # 在这里存储初始的提示文字，以便后续重置使用
        self.initial_epub_text = "Import EPUB here"
        self.initial_image_text = "Import jpg here"

        self.epub_label = ttk.Label(self.epub_frame, text=self.initial_epub_text, anchor="center", font=('Helvetica', 12))
        self.epub_label.pack(expand=True)

        self.epub_status_label = ttk.Label(self, text="EPUB not imported")
        self.epub_status_label.pack(fill="x", padx=10, pady=5)

        # EPUB处理按钮
        self.process_epub_button = ttk.Button(self, text="Process EPUB", style='ButtonNo1.TButton', command=self.process_epub)
        self.process_epub_button.pack(fill="x", padx=100, pady=5)

        # 图片预览区域（可拖放）
        self.preview_frame = ttk.Frame(self, width=380, height=200, style='DropZone.TFrame')
        self.preview_frame.pack(pady=10, padx=10)
        self.preview_frame.pack_propagate(False)

        self.preview_label = ttk.Label(self.preview_frame, text=self.initial_image_text, anchor="center", font=('Helvetica', 12))
        self.preview_label.pack(expand=True)

        self.image_status_label = ttk.Label(self, text="Images not imported")
        self.image_status_label.pack(fill="x", padx=10, pady=5)

        # 图片处理控件
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", pady=5)

        ttk.Checkbutton(control_frame, text="Right to Left", variable=self.desc_order,
                        command=self.reorder_images).pack(side=tk.LEFT, padx=(100, 10))

        self.stitch_button = ttk.Button(control_frame, text="Stitch images", style='ButtonNo2.TButton', command=self.stitch_images)
        self.stitch_button.pack(side=tk.LEFT)

        # 通用功能按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=10)

        self.clear_button = ttk.Button(button_frame, text="Clear", style='ButtonNo4.TButton', command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, expand=True, fill="x", padx=(50, 5))

        self.pack_button = ttk.Button(button_frame, text="Pack to digital", style='ButtonNo3.TButton', command=self.pack_to_digital)
        self.pack_button.pack(side=tk.LEFT, expand=True, fill="x", padx=(5, 50))


        # 启用拖放功能
        self.epub_frame.drop_target_register(DND_FILES)
        self.epub_frame.dnd_bind('<<Drop>>', self.drop_epub)

        self.preview_frame.drop_target_register(DND_FILES)
        self.preview_frame.dnd_bind('<<Drop>>', self.drop_images)

    def drop_epub(self, event):
        file_path = event.data.strip("{}")
        if file_path.lower().endswith('.epub'):
            self.epub_file = os.path.normpath(file_path)
            self.epub_status_label.config(text=f"IMPORTED: {os.path.basename(self.epub_file)}")
            self.epub_label.config(text="EPUB imported")
        else:
            messagebox.showerror("ERROR", "Please import EPUB here.")

    def drop_images(self, event):
        paths = self.tk.splitlist(event.data)
        self.process_new_images(paths)
        self.update_image_status()

    def process_new_images(self, paths):
        valid_paths = [p for p in paths if p.lower().endswith(('.jpg', '.jpeg', '.png'))]
        remaining_slots = self.max_images - len(self.image_paths)
        if remaining_slots > 0:
            new_paths = valid_paths[:remaining_slots]
            self.image_paths.extend(new_paths)
            self.reorder_images()
            self.update_image_status()
            self.show_images()  # 添加这行来显示预览
        else:
            messagebox.showinfo("maximum of images reached", "maximum of 2 images")
    
    def show_images(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if not self.image_paths:
            self.preview_label = ttk.Label(self.preview_frame, text=self.initial_image_text, anchor="center", font=('Helvetica', 12))
            self.preview_label.pack(expand=True)
            return

        for i, path in enumerate(self.image_paths):
            img = Image.open(path)
            img.thumbnail((180, 180))  # 调整预览图片大小
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(self.preview_frame, image=photo)
            label.image = photo  # 保持对图片的引用
            label.pack(side=tk.LEFT, padx=5, expand=True)

    def update_image_status(self):
        if not self.image_paths:
            self.image_status_label.config(text="0 image imported")
            self.preview_label.config(text= self.initial_image_text)  # 当没有图片时重置文字
        elif len(self.image_paths) == 1:
            self.image_status_label.config(text="1 image imported")
        else:
            self.image_status_label.config(text="2 images imported")

    def reorder_images(self):
        if len(self.image_paths) == 2:
            self.image_paths.sort(key=lambda p: self.extract_number(p), reverse=self.desc_order.get())
        self.update_image_status()
        self.show_images()  # 添加这行来更新预览

    def extract_number(self, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        number = re.sub(r'^0+', '', filename)
        return int(number) if number.isdigit() else filename

    def update_preview(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if not self.image_paths:
            self.preview_label = ttk.Label(self.preview_frame, text=self.initial_image_text, anchor="center", font=('Helvetica', 12))
            self.preview_label.pack(expand=True)
            self.image_status_label.config(text="0 image imported")
        else:
            for i, path in enumerate(self.image_paths):
                img = Image.open(path)
                img.thumbnail((180, 180))
                photo = ImageTk.PhotoImage(img)
                label = ttk.Label(self.preview_frame, image=photo)
                label.image = photo
                label.pack(side=tk.LEFT, padx=5, expand=True)
            self.image_status_label.config(text=f"{len(self.image_paths)} image(s) imported")


    def process_epub(self):
        if not self.epub_file:
            messagebox.showerror("ERROR", "No EPUB imported")
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
            # messagebox.showinfo("Completed", "EPUB Processed")
            self.clear_epub()
        except Exception as e:
            messagebox.showerror("ERROR", f"Error processing EPUB file: {e}")
            self.clear_epub()

    def clear_epub(self):
        self.epub_file = None
        self.epub_label.config(text=self.initial_epub_text)
        self.epub_status_label.config(text="No EPUB imported")   
           
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

    def stitch_images(self):
        if len(self.image_paths) != 2:
            messagebox.showerror("ERROR", "Please add 2 images before stitching!")
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

            # messagebox.showinfo("Completed", "Images stitched successfully")
            self.after(100, self.clear_images)
        except Exception as e:
            messagebox.showerror("ERROR", f"Error while stitching images: {e}")

    def pack_to_digital(self):
        target_dir = os.path.join(OUTPUT_DIR, "digital")
        os.makedirs(target_dir, exist_ok=True)

        for item in os.listdir(OUTPUT_DIR):
            source_item = os.path.join(OUTPUT_DIR, item)
            if source_item != target_dir:
                shutil.move(source_item, os.path.join(target_dir, item))

        # messagebox.showinfo("Completed", f"All files moved {target_dir}")

    def clear_images(self):
        self.image_paths = []
        self.update_preview()

    def clear_all(self):
        self.clear_epub()
        self.clear_images()

if __name__ == "__main__":
    app = OptimizedApp()
    app.mainloop()