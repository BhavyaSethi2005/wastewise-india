"""
utils/gemini_client.py
Gemini wrapper using google-generativeai SDK (works on HF Spaces).
"""

import os, json, logging
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
logger = logging.getLogger(__name__)

MODEL = "gemini-3.5-flash"
CATEGORIES = ["organic", "dry_recyclable", "hazardous", "e_waste", "sanitary", "unknown"]


def _call(prompt: str, image: Image.Image = None) -> str:
    """Single Gemini call with 3 retries."""
    for attempt in range(3):
        try:
            model = genai.GenerativeModel(MODEL)
            contents = [prompt, image] if image else prompt
            return model.generate_content(contents).text.strip()
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                import time; time.sleep(10)
            elif attempt == 2:
                raise


def _parse(raw: str) -> dict:
    return json.loads(raw.replace("```json", "").replace("```", "").strip())


def classify_and_explain(context: str, language: str = "English",
                         image: Image.Image = None, description: str = "") -> dict:
    """One Gemini call — identify + classify + explain."""
    hindi = '"hindi_summary": "2 sentences in Hindi",' if language == "Hindi" else '"hindi_summary": "",'
    item_source = f'Item: "{description}"' if description else "Identify the item in this image."

    prompt = f"""{item_source}
India waste knowledge base:
{context}

Reply ONLY in JSON:
{{
  "item_name": "",
  "category": "organic/dry_recyclable/hazardous/e_waste/sanitary/unknown",
  "confidence": "high/medium/low",
  "why": "2 sentences why this category and harm of wrong disposal",
  "steps": ["step1", "step2", "step3"],
  "warning": "",
  {hindi}
}}"""

    try:
        result = _parse(_call(prompt, image))
        if result.get("category") not in CATEGORIES:
            result["category"] = "unknown"
        result.setdefault("item_name", description or "Unknown item")
        result.setdefault("confidence", "low")
        result.setdefault("why", "Dispose responsibly.")
        result.setdefault("steps", ["Contact your local municipal corporation."])
        result.setdefault("warning", "")
        result.setdefault("hindi_summary", "")
        return result
    except Exception as e:
        logger.error(f"Gemini failed: {e}")
        return {"item_name": description or "Unknown", "category": "unknown",
                "confidence": "low", "why": "Could not process.",
                "steps": ["Contact your local municipal corporation."],
                "warning": "", "hindi_summary": ""}


def test_connection() -> bool:
    try:
        return "ok" in _call("Reply with the single word: ok").lower()
    except Exception as e:
        logger.error(f"Gemini connection failed: {e}")
        return False