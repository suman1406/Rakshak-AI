# scripts/dedupe.py
import imagehash
from PIL import Image
from collections import defaultdict
import pathlib

def cluster_near_duplicates(image_dir: str, hash_size: int = 8):
    clusters = defaultdict(list)
    for img_path in pathlib.Path(image_dir).rglob("*.jpg"):
        h = imagehash.phash(Image.open(img_path), hash_size=hash_size)
        clusters[str(h)].append(img_path)
    return {k: v for k, v in clusters.items() if len(v) > 1}

if __name__ == "__main__":
    dupes = cluster_near_duplicates("dataset")
    print(f"{len(dupes)} near-duplicate clusters found")