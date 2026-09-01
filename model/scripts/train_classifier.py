# scripts/train_classifier.py
import pathlib, torch, timm
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SPLIT_DIR = PROJECT_ROOT / "dataset_split"
WEIGHTS_DIR = PROJECT_ROOT / "weights"
WEIGHTS_DIR.mkdir(exist_ok=True)

device = "mps" if torch.backends.mps.is_available() else "cpu"

train_tf = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.3, 0.3, 0.3),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])
val_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

train_ds = datasets.ImageFolder(SPLIT_DIR / "train", transform=train_tf)
val_ds = datasets.ImageFolder(SPLIT_DIR / "val", transform=val_tf)
class_names = train_ds.classes  # alphabetical order — this becomes classes.json order

train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=32)

# class-weighted loss from actual counts
counts = [0] * len(class_names)
for _, label in train_ds.samples:
    counts[label] += 1
total = sum(counts)
weights = torch.tensor([total / (len(counts) * c) for c in counts]).to(device)
criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.1)

model = timm.create_model("efficientnet_b0", pretrained=True, num_classes=len(class_names)).to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=30)

best_val_f1 = 0.0
for epoch in range(30):
    model.train()
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(imgs), labels)
        loss.backward()
        optimizer.step()
    scheduler.step()

    model.eval()
    correct, total_n = 0, 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            preds = model(imgs).argmax(1)
            correct += (preds == labels).sum().item()
            total_n += labels.size(0)
    val_acc = correct / total_n
    print(f"epoch {epoch}: val_acc={val_acc:.3f}")
    if val_acc > best_val_f1:
        best_val_f1 = val_acc
        torch.save(model.state_dict(), WEIGHTS_DIR / "soybean_classifier_effnet_b0.pt")

import json
json.dump(class_names, open(WEIGHTS_DIR / "classes.json", "w"))
print("class order saved:", class_names)