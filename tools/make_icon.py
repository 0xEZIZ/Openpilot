from PIL import Image
import os

def make_ico(input_path, output_path):
    img = Image.open(input_path)
    # Resize to common icon sizes
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_path, sizes=icon_sizes)
    print(f"Icon saved to {output_path}")

if __name__ == "__main__":
    make_ico("logo (2).jpg", "logo.ico")
