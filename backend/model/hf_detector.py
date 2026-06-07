import os
os.environ["TRANSFORMERS_CACHE"] = "/opt/render/project/src/.cache"
os.environ["HF_HOME"] = "/opt/render/project/src/.cache"
import torch
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification
import cv2
import os

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

_model = None
_processor = None
MODEL_NAME = "dima806/deepfake_vs_real_image_detection"

# ─── Face Detection Setup ─────────────────────────────────────────────────────
# Load multiple Haar cascades for robust face detection
_face_cascades = []


def _init_face_detectors():
    global _face_cascades
    cascade_files = [
        cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml",
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml",
        cv2.data.haarcascades + "haarcascade_frontalface_alt.xml",
    ]
    for cf in cascade_files:
        cascade = cv2.CascadeClassifier(cf)
        if not cascade.empty():
            _face_cascades.append(cascade)
    print(f"✅ Loaded {len(_face_cascades)} face detection cascades")


_init_face_detectors()


# ─── Model Loading ─────────────────────────────────────────────────────────────
def load_pretrained_model():
    global _model, _processor
    print(f"Loading Hugging Face deepfake model...")
    print(f"Downloading {MODEL_NAME}...")
    print(f"This may take 2-5 minutes first time...")
    _processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    _model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
    _model.to(DEVICE)
    _model.eval()
    print(f"✅ Model loaded successfully")
    print(f"   Labels: {_model.config.id2label}")


def get_model():
    global _model, _processor
    if _model is None or _processor is None:
        load_pretrained_model()
    return _model, _processor


# ─── Face Detection ────────────────────────────────────────────────────────────
def _detect_faces(image_bgr):
    """
    Detect faces in a BGR image using multiple Haar cascades.
    Returns list of (x, y, w, h) bounding boxes.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    all_faces = []
    for cascade in _face_cascades:
        # Try multiple scale factors for robustness
        for scale in [1.1, 1.2, 1.3]:
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=scale,
                minNeighbors=5,
                minSize=(60, 60),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            if len(faces) > 0:
                all_faces.extend(faces.tolist())

    if not all_faces:
        return []

    # Merge overlapping detections using groupRectangles
    all_faces_arr = np.array(all_faces)
    # Simple NMS: pick the largest face if multiple overlap
    merged = _non_max_suppression(all_faces_arr, overlap_thresh=0.4)
    return merged


def _non_max_suppression(boxes, overlap_thresh=0.4):
    """Simple non-max suppression to remove duplicate face detections."""
    if len(boxes) == 0:
        return []

    boxes = boxes.astype(float)
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 0] + boxes[:, 2]
    y2 = boxes[:, 1] + boxes[:, 3]
    areas = boxes[:, 2] * boxes[:, 3]

    # Sort by area (prefer larger detections)
    idxs = np.argsort(areas)[::-1]
    picked = []

    while len(idxs) > 0:
        i = idxs[0]
        picked.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[1:]])
        yy1 = np.maximum(y1[i], y1[idxs[1:]])
        xx2 = np.minimum(x2[i], x2[idxs[1:]])
        yy2 = np.minimum(y2[i], y2[idxs[1:]])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        overlap = (w * h) / areas[idxs[1:]]

        remove = np.where(overlap > overlap_thresh)[0]
        idxs = np.delete(idxs, np.concatenate(([0], remove + 1)))

    return boxes[picked].astype(int).tolist()


def _crop_face(image_pil, bbox, margin=0.3):
    """
    Crop a face from a PIL image with a margin around the bounding box.
    The margin helps include forehead, chin, and some context.
    """
    w_img, h_img = image_pil.size
    x, y, w, h = bbox

    # Add margin
    margin_x = int(w * margin)
    margin_y = int(h * margin)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(w_img, x + w + margin_x)
    y2 = min(h_img, y + h + margin_y)

    return image_pil.crop((x1, y1, x2, y2))


# ─── Classification ────────────────────────────────────────────────────────────
def _classify_single(pil_image):
    """
    Classify a single PIL image (should be a face crop).
    Returns the probability of being deepfake (0.0 to 1.0).
    """
    model, processor = get_model()
    inputs = processor(images=pil_image, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1)[0]

    # Model labels: {0: "Real", 1: "Fake"} (from dima806 model)
    fake_idx = 1
    labels = model.config.id2label
    for idx, label in labels.items():
        if "fake" in label.lower():
            fake_idx = int(idx)
            break
            
    fake_prob = probs[fake_idx].item()
    return fake_prob


def _classify_with_augmentation(pil_image):
    """
    Classify a face crop with test-time augmentation for more robust results.
    Returns the average fake probability across augmented versions.
    """
    crops = []
    w, h = pil_image.size

    # Original
    crops.append(pil_image)

    # Horizontal flip (faces can be asymmetric in deepfakes)
    crops.append(pil_image.transpose(Image.FLIP_LEFT_RIGHT))

    # Slight center crop (reduces border artifacts)
    if w > 100 and h > 100:
        margin = 0.05
        crops.append(pil_image.crop((
            int(w * margin), int(h * margin),
            int(w * (1 - margin)), int(h * (1 - margin))
        )))

    fake_probs = []
    for crop in crops:
        prob = _classify_single(crop)
        fake_probs.append(prob)

    return float(np.mean(fake_probs)), fake_probs


# ─── Public API ─────────────────────────────────────────────────────────────────
def predict_image(image_path: str) -> dict:
    """
    Predict whether an image is real or deepfake.
    Steps:
    1. Detect faces in the image
    2. Crop each face with margin
    3. Classify each face crop with augmentation
    4. Return overall result
    """
    try:
        # Load image
        image_pil = Image.open(image_path).convert("RGB")
        image_bgr = cv2.imread(image_path)

        if image_bgr is None:
            # Fallback: convert from PIL
            image_bgr = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

        # Step 1: Detect faces
        faces = _detect_faces(image_bgr)
        print(f"🔍 Detected {len(faces)} face(s) in image")

        if len(faces) > 0:
            # Step 2 & 3: Crop and classify each face
            face_results = []
            for i, bbox in enumerate(faces):
                face_crop = _crop_face(image_pil, bbox, margin=0.3)
                avg_fake, all_probs = _classify_with_augmentation(face_crop)
                face_results.append(avg_fake)
                print(f"   Face {i+1}: fake_prob={avg_fake:.4f} "
                      f"(augmented: {[f'{p:.4f}' for p in all_probs]})")

            # Use the highest fake probability among all faces
            # (if ANY face is fake, the image is likely manipulated)
            max_fake = max(face_results)
            avg_fake = float(np.mean(face_results))

            # Use the max for detection (conservative approach)
            final_fake_prob = max_fake
            print(f"🔍 Max fake prob: {max_fake:.4f}, "
                  f"Avg fake prob: {avg_fake:.4f}")

            if final_fake_prob > 0.5:
                prediction = "FAKE"
                confidence = round(final_fake_prob, 4)
            else:
                prediction = "REAL"
                confidence = round(1.0 - final_fake_prob, 4)
        else:
            # No face detected - return neutral result
            print("⚠️  No face detected, returning neutral fallback (0.5)")
            final_fake_prob = 0.5
            prediction = "REAL"  # Default assumption for non-face images
            confidence = 0.5

        print(f"✅ Final: {prediction} (confidence: {confidence:.4f})")

        return {
            "prediction": prediction,
            "confidence": confidence
        }

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        raise


def predict_video(video_path: str, max_frames: int = 10) -> dict:
    """
    Predict whether a video is real or deepfake.
    Steps:
    1. Sample frames from the video
    2. Detect faces in each frame
    3. Classify face crops
    4. Vote across frames for final result
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = max(1, total_frames // max_frames)
        frame_results = []
        frame_count = 0
        analyzed = 0

        print(f"🎬 Video: {total_frames} total frames, "
              f"sampling every {interval} frames")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % interval == 0 and analyzed < max_frames:
                # Detect faces in this frame
                faces = _detect_faces(frame)

                if len(faces) > 0:
                    # Classify the largest face
                    # Sort by area, pick largest
                    faces_sorted = sorted(
                        faces, key=lambda f: f[2] * f[3], reverse=True
                    )
                    bbox = faces_sorted[0]

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_frame = Image.fromarray(frame_rgb)
                    face_crop = _crop_face(pil_frame, bbox, margin=0.3)

                    fake_prob = _classify_single(face_crop)
                else:
                    # No face found in this frame, use neutral fallback
                    fake_prob = 0.5

                real_prob = 1.0 - fake_prob

                if fake_prob > 0.5:
                    pred = "FAKE"
                    conf = round(fake_prob, 4)
                else:
                    pred = "REAL"
                    conf = round(real_prob, 4)

                print(f"  Frame {frame_count}: {pred} ({conf:.4f})"
                      f" [faces: {len(faces)}]")

                frame_results.append({
                    "prediction": pred,
                    "confidence": conf,
                    "fake_prob": fake_prob
                })
                analyzed += 1

            frame_count += 1

        cap.release()

        if not frame_results:
            raise Exception("No frames analyzed")

        # Vote across frames
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
              f"(Fake frames: {fake_votes}, Real frames: {real_votes})")

        return {
            "prediction": final_prediction,
            "confidence": avg_confidence,
            "frames_analyzed": analyzed
        }

    except Exception as e:
        print(f"❌ Video error: {e}")
        import traceback
        traceback.print_exc()
        raise