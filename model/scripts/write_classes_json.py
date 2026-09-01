# scripts/write_classes_json.py
import pathlib, json
from torchvision import datasets

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPLIT_DIR = PROJECT_ROOT / "dataset_split"
WEIGHTS_DIR = PROJECT_ROOT / "weights"

train_ds = datasets.ImageFolder(SPLIT_DIR / "train")
class_names = train_ds.classes

json.dump(class_names, open(WEIGHTS_DIR / "classes.json", "w"))
print("class order:", class_names)