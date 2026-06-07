import os

os.environ["TRANSFORMERS_CACHE"] = "/opt/render/project/src/.cache"
os.environ["HF_HOME"] = "/opt/render/project/src/.cache"

from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_NAME = "dima806/deepfake_vs_real_image_detection"

print("⬇️  Downloading model weights...")
AutoImageProcessor.from_pretrained(MODEL_NAME)
AutoModelForImageClassification.from_pretrained(MODEL_NAME)
print("✅ Model downloaded and cached!")