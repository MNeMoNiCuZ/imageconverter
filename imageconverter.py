"""
Image Converter
A simple GUI application for converting images between different formats.
Supports drag-and-drop functionality and preserves image quality during conversion.

Input formats supported:
• APNG   • FTC    • JPE    • PSD    • AVIF   • FTU    • JPEG   • PXR    • AVIFS  • GBR    • JPG    • QOI    • BLP    • GIF    • JPX    • RAS    • BMP    • GRIB   • MPEG   • RGB    • BUFR   • H5     • MPG    • RGBA   • BW     • HDF    • MSP    • SGI    • CUR    • ICB    • PBM    • TGA    • DCX    • ICNS   • PCD    • TIF    • DDS    • ICO    • PCX    • TIFF   • DIB    • IIM    • VDA

Output formats available:
Formats with transparency support:
• PNG • WEBP • GIF • TIFF • AVIF

Formats without transparency:
• JPG/JPEG
• BMP
"""

import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import pillow_avif
import os

# Get all supported input formats
exts = Image.registered_extensions()
supported_extensions = {ex[1:].upper() for ex, f in exts.items() if f in Image.OPEN}
supported_extensions_list = sorted(list(supported_extensions))

def clean_filepath(filepath):
    """Clean and normalize the file path.
    
    Args:
        filepath (str): The original file path
        
    Returns:
        str: Cleaned and normalized file path
    """
    print(f"Original dropped filepath: {filepath}")
    # Remove enclosing braces (if any) and whitespace
    filepath = filepath.strip().strip("{}")
    filepath = os.path.normpath(filepath)  # Normalize slashes
    print(f"Cleaned and normalized filepath: {filepath}")
    return filepath

def convert_images(filepaths, format_choice, overwrite):
    """Convert images to the selected format.
    
    Args:
        filepaths (list): List of file paths to convert
        format_choice (tk.StringVar): Selected output format
        overwrite (tk.BooleanVar): Whether to overwrite existing files
        
    The function handles various input formats and converts them to the selected output format
    while preserving quality. Special handling is implemented for formats with alpha channels
    and for AVIF format.
    """
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
            
            # Normalize extensions
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

            # Handle different output formats with appropriate settings
            if output_format == "jpg":
                # Convert to RGB to ensure JPEG compatibility
                img.convert("RGB").save(output_file, "JPEG", quality=95)
            elif output_format == "PNG":
                # Preserve alpha channel if present
                img.save(output_file, "PNG")
            elif output_format == "webp":
                # WebP with good balance of quality and compression
                img.save(output_file, "WEBP", quality=90)
            elif output_format == "gif":
                # Handle transparency for GIF
                img = img.convert('RGBA')
                img_with_transparency = Image.new("RGBA", img.size)
                img_with_transparency.paste(img, (0, 0), img)
                img_with_transparency.convert("P", palette=Image.ADAPTIVE).save(output_file, format="GIF", transparency=0)
            elif output_format == "avif":
                # AVIF with high quality settings
                img.save(output_file, "AVIF", quality=90)
            else:
                # Default handling for other formats
                img.save(output_file, output_format.upper())

            print(f"Successfully converted {filepath} to {output_file}")
        except PermissionError:
            print(f"Permission denied for file: {filepath}. Check if the file is open or locked.")
        except Exception as e:
            print(f"Failed to convert {filepath}: {e}")


def on_drop(event):
    print(f"Raw drop event data: {event.data}")
    # Handle paths wrapped in curly braces properly
    if "{" in event.data and "}" in event.data:
        files = [event.data.strip()]
    else:
        # Split paths (assume newline or space separation for multiple files)
        files = event.data.split()
    
    # Clean file paths
    cleaned_files = [clean_filepath(f) for f in files if f]

    print(f"Files after cleaning: {cleaned_files}")

    if not cleaned_files:
        print("No valid files detected in the drop.")
        return
    
    convert_images(cleaned_files, format_choice, overwrite_var)

root = TkinterDnD.Tk()
root.title("Image Converter")
# Window size can be adjusted here to fit the format columns
root.geometry("600x500")  

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Simple instructions
label = ttk.Label(
    main_frame, 
    text="Drag and drop image files here\nFiles will be saved in the same folder",
    font=("Helvetica", 11),
    justify="center"
)
label.pack(pady=10)

# Format selection frame
format_frame = ttk.LabelFrame(main_frame, text="Output Format", padding="10")
format_frame.pack(fill=tk.X, pady=5)

# Available formats
format_choice = tk.StringVar(value="JPG")
formats = ["PNG", "JPG", "WEBP", "GIF", "BMP", "TIFF", "AVIF"]
formats_combobox = ttk.Combobox(
    format_frame, 
    textvariable=format_choice, 
    values=formats, 
    state="readonly"
)
formats_combobox.pack(fill=tk.X)

# Options frame
options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
options_frame.pack(fill=tk.X, pady=5)

overwrite_var = tk.BooleanVar(value=True)
overwrite_checkbox = ttk.Checkbutton(
    options_frame, 
    text="Overwrite existing files", 
    variable=overwrite_var
)
overwrite_checkbox.pack(pady=5)

# Input formats frame
formats_frame = ttk.LabelFrame(main_frame, text="Supported Input Formats", padding="10")
formats_frame.pack(fill=tk.BOTH, expand=True, pady=5)

# Create 4 columns for formats
columns_frame = ttk.Frame(formats_frame)
columns_frame.pack(fill=tk.BOTH, expand=True)

# Split formats into 4 columns
formats_per_column = -(-len(supported_extensions_list) // 4)  # Ceiling division
format_columns = [[] for _ in range(4)]
for i, fmt in enumerate(supported_extensions_list):
    format_columns[i // formats_per_column].append(fmt)

# Create and pack the columns
for i, column in enumerate(format_columns):
    column_frame = ttk.Frame(columns_frame)
    column_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    
    for fmt in column:
        fmt_label = ttk.Label(
            column_frame,
            text=f"• {fmt}",
            font=("Helvetica", 10)
        )
        fmt_label.pack(anchor=tk.W, padx=5)

# Register drag and drop
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
