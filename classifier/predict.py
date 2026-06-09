"""
classifier/predict.py
CNN prediction only. Gemini classification now handled in chain.py.
Returns CNN category + confidence if weights exist, else None.
"""

import torch
from torchvision import transforms
from PIL import Image
from classifier.model import load_model, CLASSES

_model = load_model()

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def cnn_predict(image: Image.Image) -> dict | None:
    """
    Run CNN on image. Returns {category, confidence} or None if no weights.
    Used by chain.py to optionally override Gemini category with faster CNN result.
    """
    if _model is None:
        return None

    tensor = _transform(image.convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(_model(tensor), dim=1)[0]

    confidence = probs.max().item()
    if confidence < 0.60:
        return None  # not confident enough

    return {"category": CLASSES[probs.argmax().item()], "confidence": f"{confidence:.0%}"}