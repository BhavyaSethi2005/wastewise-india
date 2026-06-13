"""
tests/test_rag.py
Tests FAISS index and retrieval quality.
Run: python -m pytest tests/test_rag.py -v
"""

import pytest
from rag.retriever import retrieve


def test_retrieve_returns_string():
    """retrieve() returns a non-empty string."""
    result = retrieve("plastic bottle")
    assert isinstance(result, str)
    assert len(result) > 0


def test_retrieve_finds_relevant_chunks():
    """Query for a known item returns chunks mentioning it."""
    result = retrieve("medicine blister pack")
    # Should find our confusing_items.txt entry
    assert "medicine" in result.lower() or "blister" in result.lower()


def test_retrieve_india_specific_item():
    """Query for India-specific item returns relevant context."""
    result = retrieve("agarbatti incense stick")
    assert "agarbatti" in result.lower() or "incense" in result.lower()


def test_retrieve_hazardous_item():
    """Query for hazardous item returns hazard-related context."""
    result = retrieve("CFL bulb mercury")
    assert "mercury" in result.lower() or "e-waste" in result.lower() or "hazard" in result.lower()


def test_retrieve_k_parameter():
    """k parameter controls number of returned chunks."""
    result_1 = retrieve("plastic bottle", k=1)
    result_3 = retrieve("plastic bottle", k=3)

    # More chunks (k=3) should generally return more text than k=1
    assert len(result_3) >= len(result_1)


def test_retrieve_empty_query_handled():
    """Empty or generic query doesn't crash."""
    result = retrieve("waste")
    assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])