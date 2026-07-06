import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from backend.parser import parse_transaction
from backend.categoriser import categoriser

SAMPLE_FEEDS = [
    "25/03 UBER *TRIP SYDNEY AUD 42.50",
    "PAYPAL *SPOTIFY AU 10.99",
    "AMZN MKTP AU*2K4XR9 84.00",
    "01/07 OFFICEWORKS PTY LTD CLAYTON 67.40",
    "TELSTRA BILL PAY 89.00",
    "GOOGLE ADS 2025-07-01 250.00",
    "28/06 NETFLIX.COM 22.99",
    "SQ *MARIO KART CAFE MELB 26.50",
    "ANZ LOAN REPAYMENT 1200.00",
    "CHEMIST WAREHOUSE 0421 34.95",
    "Commonwealth Bank Fee 25/06/25 12.00",
    "ADOBE *CREATIVE CLD 82.49",
]

CATEGORY_COLOURS = {
    "Travel & Transport":          "#3B82F6",
    "Software & SaaS":             "#8B5CF6",
    "Food & Dining":               "#F59E0B",
    "Office Supplies":             "#10B981",
    "Utilities & Bills":           "#6B7280",
    "Advertising & Marketing":     "#EC4899",
    "Professional Services":       "#14B8A6",
    "Banking & Finance":           "#1D4ED8",
    "Subscriptions & Entertainment": "#F97316",
    "Healthcare & Wellbeing":      "#22C55E",
    "Uncategorised":               "#9CA3AF",
}


def process(raw: str):
    if not raw.strip():
        return "", "", "", "", ""

    parsed = parse_transaction(raw)
    cat    = categoriser.categorise(parsed["vendor"])

    vendor     = parsed["vendor"] or "—"
    amount     = f"${parsed['amount']:.2f}" if parsed["amount"] is not None else "—"
    date       = parsed["date"] or "—"
    category   = cat["category"]
    confidence = f"{cat['confidence'] * 100:.1f}%"

    return vendor, amount, date, category, confidence


CSS = """
.category-box textarea { font-weight: 700; font-size: 1.1rem; }
.conf-box textarea { color: #6B7280; }
footer { display: none !important; }
"""

with gr.Blocks(title="Transaction Ledger Engine", theme=gr.themes.Soft(), css=CSS) as demo:

    gr.Markdown("""
# 🏦 Automated Transaction Ledger Engine
**Raw bank feed → Structured ledger entry — instantly, with zero external API calls.**

Paste any bank feed line below. The engine extracts the vendor, amount, and date using deterministic regex,
then classifies the transaction into an accounting category using a TF-IDF cosine similarity pipeline.
""")

    with gr.Row():
        with gr.Column(scale=3):
            raw_input = gr.Textbox(
                label="Raw Bank Feed String",
                placeholder="e.g.  25/03 UBER *TRIP SYDNEY AUD 42.50",
                lines=2,
            )
            with gr.Row():
                submit_btn = gr.Button("⚡ Process", variant="primary", scale=2)
                clear_btn  = gr.Button("Clear", scale=1)

            gr.Examples(
                examples=SAMPLE_FEEDS,
                inputs=raw_input,
                label="Click any sample to load it →",
            )

        with gr.Column(scale=2):
            gr.Markdown("### 📋 Extracted Fields")
            with gr.Row():
                out_vendor = gr.Textbox(label="Vendor", interactive=False)
                out_amount = gr.Textbox(label="Amount", interactive=False)
                out_date   = gr.Textbox(label="Date",   interactive=False)

            gr.Markdown("### 🗂️ Accounting Classification")
            out_category   = gr.Textbox(label="Category",   interactive=False, elem_classes=["category-box"])
            out_confidence = gr.Textbox(label="Confidence", interactive=False, elem_classes=["conf-box"])

    gr.Markdown("""
---
### ⚙️ How it works

| Step | Method | Why |
|---|---|---|
| Amount & Date | Deterministic regex | Sub-millisecond, 100% reliable on structured fields |
| Vendor token | Regex pre-filter (split on first digit/`*`/`/`) | Out-of-the-box NER breaks on all-caps bank strings |
| Vendor refinement | spaCy `en_core_web_sm` NER | Enhancer on the already-clean token |
| Category | TF-IDF + cosine similarity | No training data, no API calls, fully explainable |

**Zero third-party API calls · No financial data leaves this environment · 10 accounting categories**
""")

    submit_btn.click(
        fn=process,
        inputs=raw_input,
        outputs=[out_vendor, out_amount, out_date, out_category, out_confidence],
    )
    clear_btn.click(
        fn=lambda: ("", "", "", "", "", ""),
        outputs=[raw_input, out_vendor, out_amount, out_date, out_category, out_confidence],
    )

if __name__ == "__main__":
    demo.launch()
