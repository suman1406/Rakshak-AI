# scripts/calibrate.py
import pathlib, torch, timm, json
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPLIT_DIR = PROJECT_ROOT / "dataset_split"
WEIGHTS_DIR = PROJECT_ROOT / "weights"
device = "mps" if torch.backends.mps.is_available() else "cpu"

class_names = json.load(open(WEIGHTS_DIR / "classes.json"))
val_tf = transforms.Compose([
    transforms.Resize((224, 224)), transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])
val_ds = datasets.ImageFolder(SPLIT_DIR / "val", transform=val_tf)
val_loader = DataLoader(val_ds, batch_size=32)

model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=len(class_names)).to(device)
model.load_state_dict(torch.load(WEIGHTS_DIR / "soybean_classifier_effnet_b0.pt", map_location=device))
model.eval()

logits_list, labels_list = [], []
with torch.no_grad():
    for imgs, labels in val_loader:
        logits_list.append(model(imgs.to(device)))
        labels_list.append(labels.to(device))
logits = torch.cat(logits_list)
labels = torch.cat(labels_list)

T = nn.Parameter(torch.ones(1, device=device))
optimizer = torch.optim.LBFGS([T], lr=0.01, max_iter=50)
nll = nn.CrossEntropyLoss()

def closure():
    optimizer.zero_grad()
    loss = nll(logits / T, labels)
    loss.backward()
    return loss
optimizer.step(closure)

temperature = max(T.item(), 1.0)  # never let calibration increase confidence
print(f"calibrated temperature (clamped): {temperature:.3f}")
json.dump({"temperature": temperature}, open(WEIGHTS_DIR / "calibration.json", "w"))