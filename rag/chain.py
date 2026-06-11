"""
rag/chain.py
Pipeline: CNN (fast, local) → RAG retrieval → Gemini (explanation + fallback).

Flow:
- If CNN confident → use CNN category, ask Gemini only for item name + explanation
- If CNN not confident → Gemini handles full classification + explanation
"""

from PIL import Image
from classifier.predict import cnn_predict
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

    # Step 1: Try CNN first (fast, local, no API call)
    cnn_result = None
    if image is not None:
        cnn_result = cnn_predict(image)

    # Step 2: Build RAG query
    # If CNN gave us a category, use it to retrieve better context
    query = text_input if text_input.strip() else (
        f"{cnn_result['category']} waste India disposal" if cnn_result
        else "household waste item India disposal"
    )
    context = retrieve(query, k=3)

    # Step 3: Gemini call
    # If CNN confident → tell Gemini the category, just ask for name + explanation
    # If CNN not confident → Gemini does full classification + explanation
    if cnn_result:
        # CNN already knows category — hint Gemini so it focuses on explanation
        hint = f"\nNote: This item has been pre-classified as {cnn_result['category']} waste with {cnn_result['confidence']} confidence."
        result = classify_and_explain(
            context=context + hint,
            language=language,
            image=image,
            description=text_input
        )
        # Trust CNN category over Gemini for organic/dry_recyclable
        result["category"]   = cnn_result["category"]
        result["confidence"] = cnn_result["confidence"]
        result["source"]     = "cnn+gemini"
    else:
        result = classify_and_explain(
            context=context,
            language=language,
            image=image,
            description=text_input
        )
        result["source"] = "gemini_only"

    # Step 4: City-specific bin guidance
    bin_guidance          = get_bin_guidance(result["category"], city)
    result["bin_color"]   = bin_guidance["bin_color"]
    result["bin_label"]   = bin_guidance["bin_label"]
    result["bin_display"] = bin_guidance["display_label"]
    result["city_action"] = bin_guidance["action"]

    # Step 5: Update session history
    history = add_entry(
        history, result["item_name"],
        result["category"], bin_guidance["bin_label"]
    )

    return result, history