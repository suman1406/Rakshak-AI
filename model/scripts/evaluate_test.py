# scripts/evaluate_test.py
import pathlib, torch, timm, json
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from collections import defaultdict

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPLIT_DIR = PROJECT_ROOT / "dataset_split"
WEIGHTS_DIR = PROJECT_ROOT / "weights"
device = "mps" if torch.backends.mps.is_available() else "cpu"

class_names = json.load(open(WEIGHTS_DIR / "classes.json"))

test_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])
test_ds = datasets.ImageFolder(SPLIT_DIR / "test", transform=test_tf)
test_loader = DataLoader(test_ds, batch_size=32)

model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=len(class_names)).to(device)
model.load_state_dict(torch.load(WEIGHTS_DIR / "soybean_classifier_effnet_b0.pt", map_location=device))
model.eval()

# confusion matrix as nested dict: confusion[true_class][predicted_class] = count
confusion = defaultdict(lambda: defaultdict(int))
class_totals = defaultdict(int)

with torch.no_grad():
    for imgs, labels in test_loader:
        preds = model(imgs.to(device)).argmax(1).cpu()
        for true_idx, pred_idx in zip(labels, preds):
            true_name = class_names[true_idx.item()]
            pred_name = class_names[pred_idx.item()]
            confusion[true_name][pred_name] += 1
            class_totals[true_name] += 1

print(f"{'Class':<28} {'Recall':>8}  {'N':>5}")
print("-" * 45)
for cname in class_names:
    correct = confusion[cname][cname]
    total = class_totals[cname]
    recall = correct / total if total else float("nan")
    flag = "  <-- WATCH" if cname == "soybean_rust" and recall < 0.85 else ""
    print(f"{cname:<28} {recall:>8.3f}  {total:>5}{flag}")

print("\nFull confusion matrix (true -> predicted counts):")
for true_name in class_names:
    row = {p: confusion[true_name][p] for p in class_names if confusion[true_name][p] > 0}
    print(f"  {true_name}: {row}")