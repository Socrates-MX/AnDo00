from PIL import Image, ImageChops
import os

def prepare_favicons(input_path, output_dir):
    img = Image.open(input_path).convert("RGBA")
    
    # Trim transparency/whitespace
    bg = Image.new(img.mode, img.size, (0,0,0,0))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
    
    # Remove padding to maximize size (0% margin)
    w, h = img.size
    max_side = max(w, h)
    new_img = Image.new("RGBA", (max_side, max_side), (255, 255, 255, 0))
    offset = ((max_side - w) // 2, (max_side - h) // 2)
    new_img.paste(img, offset)
    
    # Save versions
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    new_img.resize((16, 16), Image.Resampling.LANCZOS).save(os.path.join(output_dir, "favicon-16x16.png"))
    new_img.resize((32, 32), Image.Resampling.LANCZOS).save(os.path.join(output_dir, "favicon-32x32.png"))
    new_img.resize((180, 180), Image.Resampling.LANCZOS).save(os.path.join(output_dir, "apple-touch-icon.png"))
    
    # Save a master one for Streamlit standard
    new_img.save(os.path.join(output_dir, "favicon_master.png"))
    print("Favicons generated successfully.")

if __name__ == "__main__":
    prepare_favicons(
        "c:/Repo/AnDo00/data/favicon_new_test.png",
        "c:/Repo/AnDo00/data/favicons"
    )
