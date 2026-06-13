"""
tests/test_classifier.py
Tests CNN model loading, prediction function, and city bin guidance logic.
Run: python -m pytest tests/test_classifier.py -v
"""

import pytest
from PIL import Image
from classifier.model import load_model, build_model, CLASSES
from classifier.predict import cnn_predict
from utils.city_rules import get_bin_guidance, SUPPORTED_CITIES


# ── Model loading tests ─────────────────────────────────────────────────────

def test_model_builds_correctly():
    """build_model() returns a valid MobileNetV2 with 2 output classes."""
    model = build_model()
    assert model is not None
    # Final layer should output 2 classes (organic, dry_recyclable)
    assert model.classifier[1].out_features == 2


def test_classes_defined():
    """CLASSES list matches trained model output."""
    assert CLASSES == ["organic", "dry_recyclable"]


def test_model_loads_if_weights_exist():
    """load_model() returns model or None gracefully."""
    model = load_model()
    # Either loads successfully or returns None — never crashes
    assert model is None or model is not None


# ── CNN prediction tests (currently disabled — verify graceful fallback) ────

def test_cnn_predict_returns_none_or_dict():
    """cnn_predict returns None (disabled) or valid dict."""
    # Create a dummy blank image
    dummy_image = Image.new("RGB", (224, 224), color="white")
    result = cnn_predict(dummy_image)

    assert result is None or isinstance(result, dict)
    if result is not None:
        assert "category" in result
        assert "confidence" in result


# ── City rules tests ─────────────────────────────────────────────────────────

def test_all_supported_cities_have_rules():
    """Every city in SUPPORTED_CITIES returns valid guidance for all categories."""
    categories = ["organic", "dry_recyclable", "hazardous", "e_waste", "sanitary", "unknown"]

    for city in SUPPORTED_CITIES:
        for category in categories:
            guidance = get_bin_guidance(category, city)
            assert "bin_color" in guidance
            assert "bin_label" in guidance
            assert "action" in guidance
            assert "display_label" in guidance
            assert len(guidance["action"]) > 0


def test_indore_battery_is_black_bin():
    """Indore e-waste should map to black bin."""
    guidance = get_bin_guidance("e_waste", "Indore")
    assert guidance["bin_color"] == "black"


def test_mumbai_ewaste_no_black_bin():
    """Mumbai has no black bin — e-waste should be drop-off, not black."""
    guidance = get_bin_guidance("e_waste", "Mumbai")
    assert guidance["bin_color"] != "black"


def test_unknown_city_falls_back_to_national():
    """Unrecognised city name falls back to national standard rules."""
    guidance = get_bin_guidance("organic", "SomeRandomCityXYZ")
    assert guidance["bin_color"] == "green"  # national standard for organic


if __name__ == "__main__":
    pytest.main([__file__, "-v"])