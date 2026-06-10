"""
rag/chain.py
RAG pipeline — retrieve context first, then ONE Gemini call for everything.
"""

from PIL import Image
from rag.retriever import retrieve
from utils.gemini_client import classify_and_explain
from utils.history import add_entry
from utils.city_rules import get_bin_guidance


def run_pipeline(
    image: Image.Image = None,
    text_input: str = "",
    language: str = "English",
    city: str = "Other (National Standard)",
    history: list = None
) -> tuple[dict, list]:

    if history is None:
        history = []

    if image is None and not text_input.strip():
        return {"error": "Please upload an image or describe the item."}, history

    # Step 1: Retrieve context (local, instant)
    query   = text_input if text_input.strip() else "household waste item India disposal"
    context = retrieve(query, k=3)

    # Step 2: ONE Gemini call — classify + explain together
    result = classify_and_explain(
        context=context,
        language=language,
        image=image,
        description=text_input
    )

    # Step 3: City-specific bin guidance
    bin_guidance          = get_bin_guidance(result["category"], city)
    result["bin_color"]   = bin_guidance["bin_color"]
    result["bin_label"]   = bin_guidance["bin_label"]
    result["bin_display"] = bin_guidance["display_label"]
    result["city_action"] = bin_guidance["action"]

    # Step 4: Update session history
    history = add_entry(history, result["item_name"], result["category"], bin_guidance["bin_label"])

    return result, history