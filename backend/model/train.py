import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, WeightedRandomSampler, Subset
import os
import sys
import numpy as np
import random

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {DEVICE}")

DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "deepfake_model.pth")

EPOCHS = 5
BATCH_SIZE = 32
IMAGE_SIZE = 224
LEARNING_RATE = 0.0001
MAX_PER_CLASS = 12000

train_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.3, contrast=0.3),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

val_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])


class DeepfakeDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b0(
            weights=models.EfficientNet_B0_Weights.DEFAULT
        )
        num_features = self.model.classifier[1].in_features
        self.model.classifier = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(256, 2)
        )

    def forward(self, x):
        return self.model(x)


def get_balanced_subset(dataset, max_per_class):
    class_indices = {}
    for idx, (_, label) in enumerate(dataset.samples):
        if label not in class_indices:
            class_indices[label] = []
        class_indices[label].append(idx)

    balanced_indices = []
    for label, indices in class_indices.items():
        if len(indices) > max_per_class:
            indices = random.sample(indices, max_per_class)
        balanced_indices.extend(indices)

    random.shuffle(balanced_indices)

    for label, indices in class_indices.items():
        print(f"  Class {label} ({dataset.classes[label]}): "
              f"{min(len(indices), max_per_class)} samples")

    return Subset(dataset, balanced_indices)


def train():
    print(f"\n{'='*50}")
    print(f"DEEPFAKE DETECTOR - BALANCED TRAINING")
    print(f"{'='*50}")
    print(f"Max per class: {MAX_PER_CLASS}")
    print(f"This fixes the imbalance problem")
    print(f"{'='*50}\n")

    full_train = datasets.ImageFolder(
        root=os.path.join(DATASET_DIR, 'train'),
        transform=train_transform
    )
    full_val = datasets.ImageFolder(
        root=os.path.join(DATASET_DIR, 'val'),
        transform=val_transform
    )

    print(f"Classes: {full_train.classes}")
    print(f"Mapping: {full_train.class_to_idx}")
    print(f"\nBalancing training data...")

    train_dataset = get_balanced_subset(full_train, MAX_PER_CLASS)
    val_dataset = get_balanced_subset(full_val, MAX_PER_CLASS // 5)

    print(f"\nTotal train samples: {len(train_dataset)}")
    print(f"Total val samples: {len(val_dataset)}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    model = DeepfakeDetector().to(DEVICE)

    if os.path.exists(MODEL_SAVE_PATH):
        try:
            model.load_state_dict(
                torch.load(MODEL_SAVE_PATH, map_location=DEVICE)
            )
            print(f"\n✅ Loaded existing model")
        except Exception as e:
            print(f"\n⚠️  Starting fresh: {e}")
    else:
        print("\n⚠️  Starting fresh")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.01
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=EPOCHS
    )

    best_val_accuracy = 0.0

    for epoch in range(EPOCHS):
        print(f"\n📊 Epoch {epoch+1}/{EPOCHS}")
        print("-" * 40)

        model.train()
        train_correct = 0
        train_total = 0
        train_loss = 0.0

        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                model.parameters(), max_norm=1.0
            )
            optimizer.step()

            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

            if batch_idx % 30 == 0:
                acc = 100.0 * train_correct / max(train_total, 1)
                print(f"  Batch {batch_idx}/{len(train_loader)} "
                      f"Loss: {loss.item():.4f} "
                      f"Acc: {acc:.1f}%")

        train_acc = 100.0 * train_correct / train_total
        print(f"\n  Train Accuracy: {train_acc:.2f}%")

        model.eval()
        val_correct = 0
        val_total = 0
        fake_correct = 0
        fake_total = 0
        real_correct = 0
        real_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(DEVICE)
                labels = labels.to(DEVICE)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

                for i in range(len(labels)):
                    if labels[i] == 0:
                        fake_total += 1
                        if predicted[i] == 0:
                            fake_correct += 1
                    else:
                        real_total += 1
                        if predicted[i] == 1:
                            real_correct += 1

        val_acc = 100.0 * val_correct / val_total
        fake_acc = 100.0 * fake_correct / max(fake_total, 1)
        real_acc = 100.0 * real_correct / max(real_total, 1)

        print(f"  Val Accuracy:  {val_acc:.2f}%")
        print(f"  Fake Accuracy: {fake_acc:.2f}%")
        print(f"  Real Accuracy: {real_acc:.2f}%")

        if val_acc > best_val_accuracy:
            best_val_accuracy = val_acc
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"  💾 Best model saved: {val_acc:.2f}%")

        scheduler.step()

    print(f"\n{'='*50}")
    print(f"TRAINING COMPLETE")
    print(f"Best Accuracy: {best_val_accuracy:.2f}%")
    print(f"{'='*50}")
    print(f"\n📌 Copy deepfake_model.pth to backend folder")
    print(f"📌 Restart backend to load new model")


if __name__ == '__main__':
    train()