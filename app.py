"""
app.py — WasteWise India
"""

import gradio as gr
from PIL import Image
from rag.chain import run_pipeline
from utils.history import format_history, get_stats, create_history
from utils.gemini_client import test_connection
from utils.city_rules import SUPPORTED_CITIES

# Build FAISS index on startup if not exists (needed for HF Spaces)

    
BIN_CARD = {
    "green":    "🟢 GREEN BIN",
    "blue":     "🔵 BLUE BIN",
    "red":      "🔴 RED BIN",
    "black":    "⚫ BLACK BIN",
    "yellow":   "🟡 YELLOW BIN",
    "separate": "⚠️ NO SPECIFIC BIN",
}


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

    # Top — bin color
    bin_card = f"# {BIN_CARD.get(result['bin_color'], '⚠️ NO SPECIFIC BIN')}"

    # Item name + what to do (city action prominent)
    detail = f"""**{result['item_name']}** · {result['category'].replace('_',' ').title()}

**📍 What to do in {city}:**
{result['city_action']}"""

    # Why
    why = result["why"]
    if language == "Hindi" and result.get("hindi_summary"):
        why += f"\n\n🇮🇳 {result['hindi_summary']}"

    # Steps + warning
    steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(result["steps"]))
    if result["warning"]:
        steps += f"\n\n⚠️ {result['warning']}"

    return (bin_card, detail, why, steps,
            format_history(updated_history), get_stats(updated_history), updated_history)


def clear_all():
    return None, "", "English", "Other", [], "", "", "", "", create_history()


with gr.Blocks(title="WasteWise India", theme=gr.themes.Soft()) as app:

    history_state = gr.State(create_history())
    gr.Markdown("# 🗑️ WasteWise India\nPhoto any waste item → know which bin instantly.")

    with gr.Tabs():
        with gr.Tab("📸 Classify"):
            with gr.Row():
                with gr.Column(scale=1):
                    image_input = gr.Image(label="Upload photo", height=250)
                    text_input  = gr.Textbox(label="Or describe the item",
                                             placeholder="e.g. medicine strip, broken CFL bulb...")
                    with gr.Row():
                        city     = gr.Dropdown(SUPPORTED_CITIES, value="Other", label="Your City")
                        language = gr.Radio(["English", "Hindi"], value="English", label="Language")
                    with gr.Row():
                        classify_btn = gr.Button("🔍 Classify", variant="primary")
                        clear_btn    = gr.Button("🔄 Clear")

                with gr.Column(scale=1):
                    bin_output    = gr.Markdown()   # BIG bin — top
                    detail_output = gr.Markdown()   # item + what to do
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

| City | E-Waste | Hazardous | Sanitary |
|------|---------|-----------|---------|
| Indore | ⚫ Black bin | 🔴 Red bin | 🟡 Yellow bin |
| Delhi | ⚠️ Drop-off point | 🔴 Red bin | Separate |
| Mumbai | ⚠️ Drop-off point | Separate | Separate |
| Bengaluru | ⚠️ Drop-off point | 🔴 Red bin | Separate |
| Others | ⚠️ Nearest town | Separate | Separate |
            """)

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