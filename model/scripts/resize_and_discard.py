# scripts/resize_and_discard.py
from PIL import Image
import pathlib

TARGET_SIZE = 320
JPEG_QUALITY = 85

def resize_in_place(class_dir: str):
    for img_path in pathlib.Path(class_dir).glob("*.jpg"):
        img = Image.open(img_path).convert("RGB")
        img.thumbnail((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
        img.save(img_path, "JPEG", quality=JPEG_QUALITY)