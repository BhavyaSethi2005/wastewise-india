"""
classifier/predict.py
CNN predicts organic/dry_recyclable with confidence.
For hazardous, e_waste, sanitary — Gemini handles everything.
If CNN confidence < threshold — Gemini handles everything.
"""

import torch
from torchvision import transforms
from PIL import Image
from classifier.model import load_model, CLASSES

# Load once at module level
_model = load_model()

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

CONFIDENCE_THRESHOLD = 0.85  # high threshold — only use CNN when very confident


def cnn_predict(image: Image.Image) -> dict | None:
    """
    CNN disabled until trained on all 5 waste categories.
    Currently returns None — Gemini handles all classification.
    """
    return None