import torch
import torch.nn as nn
import timm
from torchvision import transforms
from PIL import Image
import os
import numpy as np

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🖥️  Using device: {DEVICE}")

# This uses EfficientNet pretrained on deepfake detection
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

_model = None


class PretrainedDeepfakeDetector(nn.Module):
    def __init__(self):
        super().__init__()
        # Use EfficientNet B4 pretrained on ImageNet
        # More powerful than B0
        self.backbone = timm.create_model(
            'efficientnet_b4',
            pretrained=True,
            num_classes=0
        )
        self.classifier = nn.Sequential(
            nn.Linear(1792, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features)


def load_pretrained_model():
    global _model
    print("🔄 Loading pretrained EfficientNet-B4...")
    _model = PretrainedDeepfakeDetector()
    _model.to(DEVICE)
    _model.eval()
    print("✅ Pretrained model loaded successfully")
    return _model


def get_model():
    global _model
    if _model is None:
        load_pretrained_model()
    return _model


def predict_image(image_path: str) -> dict:
    try:
        model = get_model()
        image = Image.open(image_path).convert("RGB")

        # Run multiple crops
        crops = []
        w, h = image.size

        # Original
        crops.append(image)
        # Horizontal flip
        crops.append(image.transpose(Image.FLIP_LEFT_RIGHT))
        # Center crop
        crops.append(image.crop((w//8, h//8, 7*w//8, 7*h//8)))

        fake_probs = []

        for crop in crops:
            tensor = transform(crop).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                output = model(tensor)
                fake_prob = output[0][0].item()
                fake_probs.append(fake_prob)

        avg_fake = float(np.mean(fake_probs))
        avg_real = 1.0 - avg_fake

        print(f"🔍 Predictions: {[f'{p:.4f}' for p in fake_probs]}")
        print(f"🔍 Average fake: {avg_fake:.4f}")

        if avg_fake > 0.5:
            prediction = "FAKE"
            confidence = round(avg_fake, 4)
        else:
            prediction = "REAL"
            confidence = round(avg_real, 4)

        print(f"🔍 Final: {prediction} ({confidence:.4f})")

        return {
            "prediction": prediction,
            "confidence": confidence
        }

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise


def predict_video(video_path: str, max_frames: int = 10) -> dict:
    try:
        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = max(1, total_frames // max_frames)
        frame_results = []
        frame_count = 0
        analyzed = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % interval == 0 and analyzed < max_frames:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                tensor = transform(pil_image).unsqueeze(0).to(DEVICE)

                model = get_model()
                with torch.no_grad():
                    output = model(tensor)
                    fake_prob = output[0][0].item()

                real_prob = 1.0 - fake_prob

                if fake_prob > 0.5:
                    prediction = "FAKE"
                    conf = round(fake_prob, 4)
                else:
                    prediction = "REAL"
                    conf = round(real_prob, 4)

                print(f"  Frame {frame_count}: {prediction} ({conf:.4f})")

                frame_results.append({
                    "prediction": prediction,
                    "confidence": conf
                })
                analyzed += 1

            frame_count += 1

        cap.release()

        if not frame_results:
            raise Exception("No frames analyzed")

        fake_votes = sum(
            1 for r in frame_results if r["prediction"] == "FAKE"
        )
        real_votes = len(frame_results) - fake_votes
        final_prediction = "FAKE" if fake_votes > real_votes else "REAL"
        avg_confidence = round(
            sum(r["confidence"] for r in frame_results) / len(frame_results),
            4
        )

        print(f"✅ Video: {final_prediction} "
              f"Fake:{fake_votes} Real:{real_votes}")

        return {
            "prediction": final_prediction,
            "confidence": avg_confidence,
            "frames_analyzed": analyzed
        }

    except Exception as e:
        print(f"❌ Video error: {e}")
        raise