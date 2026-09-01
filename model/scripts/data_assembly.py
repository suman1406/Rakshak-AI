# scripts/data_assembly.py
import shutil, pathlib, yaml
from resize_and_discard import resize_in_place

TAXONOMY = yaml.safe_load(open("taxonomy/class_manifest.yaml"))

def assemble_source(source_name: str, raw_dir: str, output_root: str):
    mapping = TAXONOMY[source_name]
    for raw_class_dir in pathlib.Path(raw_dir).iterdir():
        if not raw_class_dir.is_dir():
            continue
        target = mapping.get(raw_class_dir.name.lower())
        if target in (None, "drop"):
            continue
        target = "unknown_other" if target == "other" else target
        out_dir = pathlib.Path(output_root) / target
        out_dir.mkdir(parents=True, exist_ok=True)   # <-- auto-creates dataset/ subfolders
        for i, img_path in enumerate(raw_class_dir.glob("*.jpg")):
            shutil.copy(img_path, out_dir / f"{source_name}_{i:05d}.jpg")
        resize_in_place(str(out_dir))
    shutil.rmtree(raw_dir)   # deletes raw_downloads/asdid/ entirely

if __name__ == "__main__":
    assemble_source("asdid", "raw_downloads/asdid", "dataset")