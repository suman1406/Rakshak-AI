# scripts/split.py
import pathlib, random, shutil

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset"
SPLIT_DIR = PROJECT_ROOT / "dataset_split"
RATIOS = {"train": 0.8, "val": 0.1, "test": 0.1}

def split_class(class_dir: pathlib.Path, seed: int = 42):
    files = list(class_dir.glob("*.jpg"))
    random.seed(seed)
    random.shuffle(files)
    n = len(files)
    n_train = int(n * RATIOS["train"])
    n_val = int(n * RATIOS["val"])
    splits = {
        "train": files[:n_train],
        "val": files[n_train:n_train + n_val],
        "test": files[n_train + n_val:],
    }
    for split_name, split_files in splits.items():
        out_dir = SPLIT_DIR / split_name / class_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)
        for f in split_files:
            shutil.copy(f, out_dir / f.name)
    print(f"{class_dir.name}: train={len(splits['train'])} val={len(splits['val'])} test={len(splits['test'])}")

if __name__ == "__main__":
    for class_dir in DATASET_DIR.iterdir():
        if class_dir.is_dir():
            split_class(class_dir)