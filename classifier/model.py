"""
classifier/model.py
Loads fine-tuned MobileNetV2 for waste image classification.
Weights loaded from model_weights/wastenet_v1.pth (trained in Colab).
"""

import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path

# 5 waste categories our model is trained on
CLASSES = ["organic", "dry_recyclable"]
WEIGHTS_PATH = Path("model_weights/wastenet_v1.pth")


def build_model() -> nn.Module:
    """Build MobileNetV2 with custom output layer for 5 classes."""
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, 2)
    return model


def load_model() -> nn.Module | None:
    """
    Load trained weights. Returns model if weights exist, None otherwise.
    None triggers fallback to Gemini-only classification in predict.py.
    """
    if not WEIGHTS_PATH.exists():
        return None

    model = build_model()
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
    model.eval()
    return model