"""
app.py — WasteWise India
"""

import gradio as gr
from PIL import Image
from rag.chain import run_pipeline
from utils.history import format_history, get_stats, create_history
from utils.gemini_client import test_connection
from utils.city_rules import SUPPORTED_CITIES
from utils.geocoder import coords_to_city

BIN_CARD = {
    "green":    "🟢 GREEN BIN",
    "blue":     "🔵 BLUE BIN",
    "red":      "🔴 RED BIN",
    "black":    "⚫ BLACK BIN",
    "yellow":   "🟡 YELLOW BIN",
    "separate": "⚠️ NO SPECIFIC BIN",
}

# JavaScript to get browser GPS location
# Calls back to a hidden textbox with "lat,lng" string
GEOLOCATION_JS = """
() => {
    return new Promise((resolve) => {
        if (!navigator.geolocation) {
            resolve("error:not_supported");
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve(`${pos.coords.latitude},${pos.coords.longitude}`),
            (err) => resolve("error:" + err.message)
        );
    });
}
"""


def classify(image, text_input, language, city, history_state):

    if image is None and not text_input.strip():
        return "Upload an image or describe the item.", "", "", "", format_history(history_state), "", history_state

    pil_image = Image.fromarray(image) if image is not None else None

    result, updated_history = run_pipeline(
        image=pil_image, text_input=text_input,
        language=language, city=city, history=history_state
    )

    if "error" in result:
        return result["error"], "", "", "", format_history(updated_history), "", updated_history

    bin_card = f"# {BIN_CARD.get(result['bin_color'], '⚠️ NO SPECIFIC BIN')}"

    detail = f"""**{result['item_name']}** · {result['category'].replace('_',' ').title()}

**📍 What to do in {city}:**
{result['city_action']}"""

    why = result["why"]
    if language == "Hindi" and result.get("hindi_summary"):
        why += f"\n\n🇮🇳 {result['hindi_summary']}"

    steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(result["steps"]))
    if result["warning"]:
        steps += f"\n\n⚠️ {result['warning']}"

    return (bin_card, detail, why, steps,
            format_history(updated_history), get_stats(updated_history), updated_history)


def clear_all():
    return None, "", "English", "Other (National Standard)", [], "", "", "", "", create_history()


def detect_location(coords_str: str):
    """
    Called after JS returns 'lat,lng' string.
    Converts to nearest supported city and updates dropdown.
    """
    if not coords_str or coords_str.startswith("error"):
        return gr.update(), "⚠️ Could not detect location. Select city manually."

    try:
        lat, lng = map(float, coords_str.split(","))
        result = coords_to_city(lat, lng)
        city = result["city"]

        if result["exact_match"]:
            return gr.update(value=city), f"📍 Location detected: **{city}**"

        # Nearest-city fallback — show distance so user knows it's approximate
        name = result["detected_name"]
        dist = result["distance_km"]
        location_label = f" ({name})" if name else ""
        return (
            gr.update(value=city),
            f"📍 Your area{location_label} isn't directly listed — showing rules for "
            f"nearest covered city **{city}** (~{dist} km away)."
        )

    except Exception:
        return gr.update(), "⚠️ Could not detect location. Select city manually."


with gr.Blocks(title="WasteWise India", theme=gr.themes.Soft()) as app:

    history_state = gr.State(create_history())
    coords_box = gr.Textbox(visible=False)  # hidden — receives JS GPS result

    gr.Markdown("""# 🗑️ WasteWise India
Photo any waste item → know which bin instantly.

_Powered by Gemini 3.1 Flash · Free to use · No login required · 19 Indian cities covered_""")

    with gr.Tabs():
        with gr.Tab("📸 Classify"):
            with gr.Row():
                with gr.Column(scale=1):
                    image_input = gr.Image(label="Upload photo", height=250)
                    text_input  = gr.Textbox(label="Or describe the item",
                                             placeholder="e.g. medicine strip, broken CFL bulb...")
                    with gr.Row():
                        city     = gr.Dropdown(SUPPORTED_CITIES, value="Other (National Standard)",
                                               label="Your City", allow_custom_value=True)
                        language = gr.Radio(["English", "Hindi"], value="English", label="Language")

                    with gr.Row():
                        locate_btn = gr.Button("📍 Detect My City", size="sm")
                    location_status = gr.Markdown()

                    with gr.Row():
                        classify_btn = gr.Button("🔍 Classify", variant="primary")
                        clear_btn    = gr.Button("🔄 Clear")

                with gr.Column(scale=1):
                    bin_output    = gr.Markdown()
                    detail_output = gr.Markdown()
                    why_output    = gr.Textbox(label="Why this category?", lines=3, interactive=False)
                    steps_output  = gr.Textbox(label="Disposal steps", lines=4, interactive=False)

        with gr.Tab("📋 History"):
            stats_display   = gr.Markdown()
            history_display = gr.Markdown()

        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
## About WasteWise India
India generates 159,000 tonnes of waste daily. Citizens know basics but fail on unusual
items — medicine strips, agarbatti ash, thermocol, paan wrappers, broken bulbs.

**Stack:** Gemini 3.1 Flash Lite · LangChain RAG · FAISS · 91 India-specific items · Gradio
**CNN:** MobileNetV2 trained on 25k images, 94% accuracy (organic/recyclable) — full
5-category training planned for v2

| City | E-Waste | Hazardous | Sanitary |
|------|---------|-----------|---------|
| Indore | ⚫ Black bin | 🔴 Red bin | 🟡 Yellow bin |
| Delhi | ⚠️ Drop-off point | 🔴 Red bin | Separate |
| Mumbai | ⚠️ Drop-off point | Separate | Separate |
| Bengaluru | ⚠️ Drop-off point | 🔴 Red bin | Separate |
| Others | ⚠️ Nearest town | Separate | Separate |
            """)

    # ── GPS detection: JS gets coords → fills hidden box → Python converts to city ──
    locate_btn.click(fn=None, inputs=None, outputs=coords_box, js=GEOLOCATION_JS)
    coords_box.change(fn=detect_location, inputs=coords_box, outputs=[city, location_status])

    classify_btn.click(
        fn=classify,
        inputs=[image_input, text_input, language, city, history_state],
        outputs=[bin_output, detail_output, why_output, steps_output,
                 history_display, stats_display, history_state]
    )
    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[image_input, text_input, language, city, history_state,
                 bin_output, detail_output, why_output, steps_output, history_state]
    )

if __name__ == "__main__":
    if not test_connection():
        print("WARNING: Gemini API not responding. Check your .env file.")
    app.launch()