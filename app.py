"""
app.py — WasteWise India
"""

import gradio as gr
from PIL import Image
from rag.chain import run_pipeline
from utils.history import format_history, get_stats, create_history
from utils.gemini_client import check_connection
from utils.city_rules import SUPPORTED_CITIES
from utils.geocoder import coords_to_city

BIN_CARD = {
    "green":    ("🟢", "Green Bin"),
    "blue":     ("🔵", "Blue Bin"),
    "red":      ("🔴", "Red Bin"),
    "black":    ("⚫", "Black Bin"),
    "yellow":   ("🟡", "Yellow Bin"),
    "separate": ("⚠️", "No Specific Bin"),
}

BIN_BG = {
    "green":    "#1e3a2a",
    "blue":     "#1e2f47",
    "red":      "#3a1e1e",
    "black":    "#2a2a2a",
    "yellow":   "#3a3520",
    "separate": "#3a2e1e",
}

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

CUSTOM_CSS = """
.gradio-container { max-width: 1100px !important; margin: auto; }
#title-block { text-align: center; padding: 1.5rem 0 1.5rem; }
#title-block h1 { font-size: 2.4rem; margin-bottom: 0.35rem; }
#title-block p { color: var(--body-text-color-subdued); font-size: 1.05rem; margin: 0; }

.input-panel, .output-panel {
    border-radius: 16px;
    padding: 1.25rem;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
}

.result-card {
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.08);
    min-height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.result-bin {
    font-size: 1.85rem;
    font-weight: 700;
    margin: 0 0 0.35rem 0;
}
.result-item {
    font-size: 1rem;
    opacity: 0.85;
    margin: 0;
}
.result-action {
    margin-top: 0.75rem;
    font-size: 0.95rem;
    opacity: 0.9;
    padding-top: 0.6rem;
    border-top: 1px solid rgba(255,255,255,0.1);
}

.ready-icon {
    width: 56px; height: 56px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    margin-bottom: 0.75rem;
}

#classify-btn { font-size: 1.05rem !important; height: 48px; font-weight: 600; }

/* Align Detect-my-city button with the language radio row */
#locate-btn { margin-top: 26px; }
"""


def classify(image, text_input, language, city, history_state):

    if image is None and not text_input.strip():
        return (
            "<div class='result-card' style='background:#3a1e1e'>"
            "<div class='ready-icon'>⚠️</div>"
            "<p class='result-bin'>No input yet</p>"
            "<p class='result-item'>Upload an image or describe the item.</p></div>",
            "", "", format_history(history_state), "", history_state
        )

    pil_image = Image.fromarray(image) if image is not None else None

    result, updated_history = run_pipeline(
        image=pil_image, text_input=text_input,
        language=language, city=city, history=history_state
    )

    if "error" in result:
        return (
            f"<div class='result-card' style='background:#3a1e1e'>"
            f"<p class='result-bin'>⚠️ Error</p>"
            f"<p class='result-item'>{result['error']}</p></div>",
            "", "", format_history(updated_history), "", updated_history
        )

    bin_color = result["bin_color"]
    emoji, label = BIN_CARD.get(bin_color, BIN_CARD["separate"])
    bg = BIN_BG.get(bin_color, BIN_BG["separate"])

    result_html = f"""
    <div class="result-card" style="background:{bg}">
        <div class="ready-icon">{emoji}</div>
        <p class="result-bin">{label}</p>
        <p class="result-item">{result['item_name']} · {result['category'].replace('_',' ').title()}</p>
        <p class="result-action">📍 <b>{city}:</b> {result['city_action']}</p>
    </div>
    """

    why = result["why"]
    if language == "Hindi" and result.get("hindi_summary"):
        why += f"\n\n🇮🇳 {result['hindi_summary']}"

    steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(result["steps"]))
    if result["warning"]:
        steps += f"\n\n⚠️ {result['warning']}"

    return (result_html, why, steps,
            format_history(updated_history), get_stats(updated_history), updated_history)


def clear_all():
    return (None, "", "English", "Other (National Standard)", [],
            "", "", "", "", create_history())


def detect_location(coords_str: str):
    if not coords_str or coords_str.startswith("error"):
        return gr.update(), "⚠️ Could not detect location. Select city manually."

    try:
        lat, lng = map(float, coords_str.split(","))
        result = coords_to_city(lat, lng)
        city = result["city"]

        if result["exact_match"]:
            return gr.update(value=city), f"📍 Location detected: **{city}**"

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


theme = gr.themes.Soft(
    primary_hue="green",
    secondary_hue="emerald",
    neutral_hue="slate",
).set(
    button_primary_background_fill="*primary_500",
    button_primary_background_fill_hover="*primary_600",
)

with gr.Blocks(title="WasteWise India", theme=theme, css=CUSTOM_CSS) as app:

    history_state = gr.State(create_history())
    coords_box = gr.Textbox(visible=False)

    gr.HTML("""
    <div id="title-block">
        <h1>🗑️ WasteWise India</h1>
        <p>Photo any waste item → know exactly which bin it goes in, instantly.</p>
    </div>
    """)

    with gr.Tabs():
        with gr.Tab("📸 Classify"):
            with gr.Row(equal_height=True):
                with gr.Column(scale=5, elem_classes="input-panel"):
                    image_input = gr.Image(label="Upload or take a photo", height=260,
                                           sources=["upload", "webcam"])
                    text_input  = gr.Textbox(label="Or describe the item",
                                             placeholder="e.g. medicine strip, broken CFL bulb...")

                    city = gr.Dropdown(SUPPORTED_CITIES, value="Other (National Standard)",
                                      label="Your city", allow_custom_value=True)

                    with gr.Row():
                        language   = gr.Radio(["English", "Hindi"], value="English",
                                              label="Language", scale=3)
                        locate_btn = gr.Button("📍 Detect my city", size="sm", scale=2, elem_id="locate-btn")

                    location_status = gr.Markdown()

                    with gr.Row():
                        classify_btn = gr.Button("🔍 Classify", variant="primary", elem_id="classify-btn", scale=3)
                        clear_btn    = gr.Button("Clear", scale=1)

                with gr.Column(scale=5, elem_classes="output-panel"):
                    result_output = gr.HTML(
                        "<div class='result-card' style='background:#23282b'>"
                        "<div class='ready-icon'>👋</div>"
                        "<p class='result-bin'>Ready when you are</p>"
                        "<p class='result-item'>Upload a photo or describe an item to get started</p></div>"
                    )
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

    locate_btn.click(fn=None, inputs=None, outputs=coords_box, js=GEOLOCATION_JS)
    coords_box.change(fn=detect_location, inputs=coords_box, outputs=[city, location_status])

    classify_btn.click(
        fn=classify,
        inputs=[image_input, text_input, language, city, history_state],
        outputs=[result_output, why_output, steps_output,
                 history_display, stats_display, history_state]
    )
    clear_btn.click(
        fn=clear_all,
        inputs=[],
        outputs=[image_input, text_input, language, city, history_state,
                 result_output, why_output, steps_output, history_state]
    )

if __name__ == "__main__":
    if not check_connection():
        print("WARNING: Gemini API not responding. Check your .env file.")
    app.launch()