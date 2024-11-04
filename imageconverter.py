import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import os
import re

def clean_filepath(filepath):
    print(f"Cleaning filepath: {filepath}")
    cleaned = re.sub(r"[{}]", "", filepath).strip()
    print(f"Cleaned filepath: {cleaned}")
    return cleaned

def convert_images(filepaths, format_choice, overwrite):
    print(f"Starting conversion with format: {format_choice.get()}, overwrite: {overwrite.get()}")
    for filepath in filepaths:
        try:
            print(f"Processing file: {filepath}")
            filepath = clean_filepath(filepath)

            if not os.path.exists(filepath):
                print(f"File does not exist: {filepath}")
                continue
            
            file_name, file_ext = os.path.splitext(filepath)
            file_ext = file_ext.lower()[1:]
            output_format = format_choice.get().lower()
            
            if file_ext == "jpeg":
                file_ext = "jpg"

            if file_ext == output_format:
                print(f"Skipping {filepath} (already in {output_format.upper()} format)")
                continue

            img = Image.open(filepath)
            output_dir = os.path.dirname(filepath)
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(filepath))[0]}.{output_format}")
            
            if not overwrite.get() and os.path.exists(output_file):
                print(f"Skipping {output_file} (file exists and overwrite is disabled)")
                continue

            print(f"Converting {filepath} to {output_format.upper()}...")

            if output_format == "jpg":
                img.convert("RGB").save(output_file, "JPEG", quality=100)
            elif output_format in ["png", "webp"]:
                img.save(output_file, output_format.upper())
            elif output_format == "gif":
                img = img.convert('RGBA')
                img_with_transparency = Image.new("RGBA", img.size)
                img_with_transparency.paste(img, (0, 0), img)
                img_with_transparency.convert("P", palette=Image.ADAPTIVE).save(output_file, format="GIF", transparency=0)
            else:
                img.save(output_file, output_format.upper())

            print(f"Successfully converted {filepath} to {output_file}")
        except PermissionError:
            print(f"Permission denied for file: {filepath}. Check if the file is open or locked.")
        except Exception as e:
            print(f"Failed to convert {filepath}: {e}")

def on_drop(event):
    print(f"Drop event data: {event.data}")
    
    # Split paths by newline or space if multiple files are dropped
    files = event.data.split() if event.data else []
    cleaned_files = [clean_filepath(f) for f in files if f]

    # Print all detected files
    print(f"Files after split and cleaning: {cleaned_files}")

    if not cleaned_files:
        print("No valid files detected in the drop. Please check the file paths.")
        return
    
    convert_images(cleaned_files, format_choice, overwrite_var)


root = TkinterDnD.Tk()
root.title("Image Converter")
root.geometry("400x250")

label = tk.Label(root, text="Drag and drop image files here\n\nImages are saved in the original folder", font=("Helvetica", 14))
label.pack(pady=20)

format_choice = tk.StringVar(value="png")
formats = ttk.Combobox(root, textvariable=format_choice, values=["jpg", "png", "gif", "bmp", "webp", "tiff"], state="readonly")
formats.pack()

overwrite_var = tk.BooleanVar(value=True)
overwrite_checkbox = tk.Checkbutton(root, text="Overwrite existing files", variable=overwrite_var)
overwrite_checkbox.pack(pady=10)

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
