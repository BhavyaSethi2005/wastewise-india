"""
tests/test_gemini.py
Tests Gemini API connection and response format.
Run: python -m pytest tests/test_gemini.py -v
"""

import pytest
from utils.gemini_client import check_connection, classify_and_explain


def test_api_key_valid():
    """API key works and Gemini responds."""
    assert check_connection() is True


def test_classify_returns_required_keys():
    """classify_and_explain returns all expected keys."""
    result = classify_and_explain(
        context="Plastic bottles are recyclable dry waste.",
        description="plastic water bottle"
    )

    required_keys = ["item_name", "category", "confidence",
                     "why", "steps", "warning", "hindi_summary"]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"


def test_classify_returns_valid_category():
    """Category must be one of the 6 allowed values."""
    valid_categories = ["organic", "dry_recyclable", "hazardous",
                        "e_waste", "sanitary", "unknown"]

    result = classify_and_explain(
        context="Banana peels are organic biodegradable waste.",
        description="banana peel"
    )

    assert result["category"] in valid_categories


def test_classify_steps_is_list():
    """Disposal steps must be a non-empty list."""
    result = classify_and_explain(
        context="Old batteries are e-waste, dispose at collection centres.",
        description="old battery"
    )

    assert isinstance(result["steps"], list)
    assert len(result["steps"]) > 0


def test_hindi_summary_when_requested():
    """When language=Hindi, hindi_summary should be non-empty."""
    result = classify_and_explain(
        context="Newspaper is dry recyclable waste.",
        description="newspaper",
        language="Hindi"
    )

    assert result["hindi_summary"] != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])