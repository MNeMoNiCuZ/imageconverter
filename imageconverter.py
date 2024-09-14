import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import os

def convert_images(filepaths, format_choice, overwrite):
    for filepath in filepaths:
        try:
            # Handle different cases of file extensions and skip if format is the same
            file_name, file_ext = os.path.splitext(filepath)
            file_ext = file_ext.lower()[1:]  # Strip the dot and make lowercase (e.g., .JPG -> jpg)

            output_format = format_choice.get().lower()

            # Treat jpeg as jpg
            if file_ext == "jpeg":
                file_ext = "jpg"  

            if file_ext == output_format:
                print(f"Skipping {filepath} (already in {output_format.upper()} format)")
                continue

            img = Image.open(filepath)

            # Define the output path
            output_file = f"{file_name}.{output_format}"
            
            # Check for overwrite option
            if not overwrite.get() and os.path.exists(output_file):
                print(f"Skipping {output_file} (file already exists and overwrite is disabled)")
                continue

            print(f"Converting {filepath} to {output_format.upper()}...")

            if output_format == "jpg":
                img.convert("RGB").save(output_file, "JPEG", quality=100)  # Handle JPG without transparency
            elif output_format in ["png", "webp"]:
                img.save(output_file, output_format.upper())  # Handle PNG, WEBP with transparency
            elif output_format == "gif":
                # Handle transparency for GIF format
                img = img.convert('RGBA')
                img_with_transparency = Image.new("RGBA", img.size)
                img_with_transparency.paste(img, (0, 0), img)
                
                img_with_transparency.convert("P", palette=Image.ADAPTIVE).save(output_file, format="GIF", transparency=0)
            else:
                img.save(output_file, output_format.upper())

            print(f"Successfully converted {filepath} to {output_file}")
        except Exception as e:
            print(f"Failed to convert {filepath}: {e}")

def on_drop(event):
    files = event.data.split()
    print(f"Files dropped: {files}")
    convert_images(files, format_choice, overwrite_var)

# Create the TkinterDnD window
root = TkinterDnD.Tk()
root.title("Image Converter")
root.geometry("400x250")

# Label with updated text
label = tk.Label(root, text="Drag and drop image files here\n\nImages are saved in the original folder", font=("Helvetica", 14))
label.pack(pady=20)

# Dropdown menu for format selection, with webp added between gif and tiff
format_choice = tk.StringVar(value="jpg")
formats = ttk.Combobox(root, textvariable=format_choice, values=["jpg", "png", "gif", "bmp", "webp", "tiff"], state="readonly")
formats.pack()

# Checkbox for Overwrite option
overwrite_var = tk.BooleanVar(value=True)  # Default is True (checked)
overwrite_checkbox = tk.Checkbutton(root, text="Overwrite existing files", variable=overwrite_var)
overwrite_checkbox.pack(pady=10)

# Bind the drop event
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
