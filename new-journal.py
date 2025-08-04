import sys
import os
import fitz
from PIL import Image

def crop_and_save(pdf_path, year, number, margin=10):
    # Create directory paths
    base_dirs = [
        f"content/issue/{year}-{number}",
        f"content_en/issue/{year}-{number}"
    ]
    
    # Create directories if they don't exist
    for dir_path in base_dirs:
        os.makedirs(dir_path, exist_ok=True)
        # Create empty _index.md files
        with open(os.path.join(dir_path, "_index.md"), 'w') as f:
            pass
    
    # Process PDF
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    
    # Render at high resolution (300 DPI)
    zoom = 4
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Calculate crop area (right half with margin)
    left = pix.width // 2 + margin
    upper = margin
    right = pix.width - margin
    lower = pix.height - margin
    
    # Validate crop dimensions
    if left >= right or upper >= lower:
        raise ValueError(f"Crop area invalid. Page size: {pix.width}x{pix.height}px, margin: {margin}px")
    
    # Crop and save to both directories
    cropped_img = img.crop((left, upper, right, lower))
    for dir_path in base_dirs:
        cropped_img.save(os.path.join(dir_path, "cover.png"))
    
    return base_dirs

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file.pdf> <year> <issue_number>")
        print("Example: python script.py magazine.pdf 2023 04")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    year = sys.argv[2]
    issue_num = sys.argv[3]
    
    try:
        directories = crop_and_save(pdf_file, year, issue_num)
        print(f"Created directory structure:")
        for d in directories:
            print(f"- {d}/")
            print(f"  - _index.md (empty)")
            print(f"  - cover.png (cropped image)")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)