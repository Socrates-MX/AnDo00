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
    
    # Add 10% padding as requested
    w, h = img.size
    padding = int(max(w, h) * 0.1)
    new_size = (w + 2*padding, h + 2*padding)
    new_img = Image.new("RGBA", new_size, (255, 255, 255, 0))
    new_img.paste(img, (padding, padding))
    
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
        "c:/Repo/AnDo00/data/favicon_getauditup_final.png",
        "c:/Repo/AnDo00/data/favicons"
    )
