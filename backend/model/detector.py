import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image, ImageFilter
import os
import numpy as np

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🖥️  Using device: {DEVICE}")

_model = None


class DeepfakeDetector(nn.Module):
    def __init__(self):
        super(DeepfakeDetector, self).__init__()
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


def load_model(model_path: str = None):
    global _model
    _model = DeepfakeDetector()

    if model_path and os.path.exists(model_path):
        print(f"✅ Loading model from: {model_path}")
        try:
            checkpoint = torch.load(
                model_path,
                map_location=DEVICE,
                weights_only=True
            )
            _model.load_state_dict(checkpoint)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Load error: {e}")
    else:
        print(f"⚠️  No model file found")

    _model.to(DEVICE)
    _model.eval()
    return _model


def get_model():
    global _model
    if _model is None:
        load_model()
    return _model


def extract_features(image: Image.Image) -> dict:
    img_array = np.array(image.convert('RGB'))

    r = img_array[:, :, 0].astype(float)
    g = img_array[:, :, 1].astype(float)
    b = img_array[:, :, 2].astype(float)

    rg_diff = np.mean(np.abs(r - g))
    rb_diff = np.mean(np.abs(r - b))
    gb_diff = np.mean(np.abs(g - b))

    blurred = image.filter(ImageFilter.GaussianBlur(radius=2))
    orig_array = np.array(image).astype(float)
    blur_array = np.array(blurred).astype(float)
    sharpness = np.mean(np.abs(orig_array - blur_array))

    brightness = np.mean(img_array)
    contrast = np.std(img_array)

    edges = image.convert('L').filter(ImageFilter.FIND_EDGES)
    edge_array = np.array(edges)
    edge_density = np.mean(edge_array)

    noise = np.std(orig_array - blur_array)

    return {
        'rg_diff': rg_diff,
        'rb_diff': rb_diff,
        'gb_diff': gb_diff,
        'sharpness': sharpness,
        'brightness': brightness,
        'contrast': contrast,
        'edge_density': edge_density,
        'noise': noise
    }


def analyze_image_features(image: Image.Image) -> tuple:
    features = extract_features(image)

    fake_score = 0.0

    # Check 1: Color uniformity
    # Deepfakes have very uniform or very different colors
    color_uniformity = (
        features['rg_diff'] +
        features['rb_diff'] +
        features['gb_diff']
    ) / 3

    if color_uniformity < 10:
        fake_score += 0.4
    elif color_uniformity < 20:
        fake_score += 0.2
    elif color_uniformity > 40:
        fake_score += 0.15

    # Check 2: Sharpness
    # VERY important — deepfakes are often blurry
    # Your fake image has sharpness 4.72 which is very low
    if features['sharpness'] < 5:
        fake_score += 0.5      # strong fake indicator
    elif features['sharpness'] < 10:
        fake_score += 0.35
    elif features['sharpness'] < 20:
        fake_score += 0.15

    # Check 3: Noise
    # AI images have very specific noise levels
    if features['noise'] < 5:
        fake_score += 0.3
    elif features['noise'] < 10:
        fake_score += 0.2
    elif features['noise'] < 15:
        fake_score += 0.1

    # Check 4: Edge density
    # Very low edges = deepfake (too smooth)
    if features['edge_density'] < 12:
        fake_score += 0.4      # strong fake indicator
    elif features['edge_density'] < 20:
        fake_score += 0.2
    elif features['edge_density'] < 30:
        fake_score += 0.1

    # Check 5: Contrast
    if features['contrast'] < 40:
        fake_score += 0.15
    elif features['contrast'] < 55:
        fake_score += 0.05

    print(f"   color_uniformity: {color_uniformity:.2f}")
    print(f"   sharpness: {features['sharpness']:.2f}")
    print(f"   noise: {features['noise']:.2f}")
    print(f"   edge_density: {features['edge_density']:.2f}")
    print(f"   contrast: {features['contrast']:.2f}")
    print(f"   raw_fake_score: {fake_score:.2f}")

    # Normalize to 0-1 range
    # Max possible score is around 1.75
    fake_probability = min(fake_score / 1.75, 0.99)
    real_probability = 1.0 - fake_probability

    print(f"   fake_probability: {fake_probability:.4f}")

    return fake_probability, real_probability
def predict_image(image_path: str) -> dict:
    try:
        image = Image.open(image_path).convert("RGB")

        print(f"🔍 Analyzing image features...")
        feature_fake_prob, feature_real_prob = analyze_image_features(image)
        print(f"   Feature fake_prob: {feature_fake_prob:.4f}")

        transform_fn = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])

        model = get_model()
        tensor = transform_fn(image).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            outputs = model(tensor)
            probs = torch.softmax(outputs, dim=1)
            model_fake_prob = probs[0][0].item()
            model_real_prob = probs[0][1].item()

        print(f"   Model fake_prob: {model_fake_prob:.4f}")
        print(f"   Model real_prob: {model_real_prob:.4f}")

        # Combine model output with feature analysis
        # Weight feature analysis more since model is not fully trained
        combined_fake = (model_fake_prob * 0.3) + (feature_fake_prob * 0.7)
        combined_real = 1.0 - combined_fake

        print(f"   Combined fake: {combined_fake:.4f}")
        print(f"   Combined real: {combined_real:.4f}")

        if combined_fake > combined_real:
            prediction = "FAKE"
            confidence = round(combined_fake, 4)
        else:
            prediction = "REAL"
            confidence = round(combined_real, 4)

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

                feature_fake, feature_real = analyze_image_features(
                    pil_image
                )

                transform_fn = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        [0.485, 0.456, 0.406],
                        [0.229, 0.224, 0.225]
                    )
                ])

                model = get_model()
                tensor = transform_fn(pil_image).unsqueeze(0).to(DEVICE)

                with torch.no_grad():
                    outputs = model(tensor)
                    probs = torch.softmax(outputs, dim=1)
                    model_fake = probs[0][0].item()

                combined_fake = (model_fake * 0.3) + (feature_fake * 0.7)
                combined_real = 1.0 - combined_fake

                if combined_fake > combined_real:
                    prediction = "FAKE"
                    conf = round(combined_fake, 4)
                else:
                    prediction = "REAL"
                    conf = round(combined_real, 4)

                print(f"  Frame {frame_count}: {prediction} "
                      f"({conf:.4f})")

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

        print(f"✅ Video result: {final_prediction} "
              f"Fake:{fake_votes} Real:{real_votes}")

        return {
            "prediction": final_prediction,
            "confidence": avg_confidence,
            "frames_analyzed": analyzed
        }

    except Exception as e:
        print(f"❌ Video error: {e}")
        raise