"""
Gradio demo for the Transaction Ledger Engine.

Run:  python frontend/app.py
Requires the backend package to be importable (run from project root).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from backend.parser import parse_transaction
from backend.categoriser import categoriser

SAMPLE_FEEDS = [
    "25/03 UBER *TRIP SYDNEY AUD 42.50",
    "PAYPAL *SPOTIFY AU 10.99",
    "AMZN MKTP AU*2K4XR9 84.00",
    "01/07 OFFICEWORKS PTY LTD CLAYTON 67.40",
    "TELSTRA BILL PAY 89.00",
    "03/07 WOOLWORTHS 3042 PRAHRAN 156.23",
    "GOOGLE ADS 2025-07-01 250.00",
    "ANZ LOAN REPAYMENT 1200.00",
    "28/06 NETFLIX.COM 22.99",
    "SQ *MARIO KART CAFE MELB 26.50",
]


def process(raw: str):
    if not raw.strip():
        return "", "", "", "", ""

    parsed = parse_transaction(raw)
    cat = categoriser.categorise(parsed["vendor"])

    vendor  = parsed["vendor"] or "—"
    amount  = f"${parsed['amount']:.2f}" if parsed["amount"] else "—"
    date    = parsed["date"] or "—"
    category = cat["category"]
    confidence = f"{cat['confidence'] * 100:.1f}%"

    return vendor, amount, date, category, confidence


with gr.Blocks(
    title="Transaction Ledger Engine",
    theme=gr.themes.Soft(),
    css=".output-label { font-size: 0.85rem; color: #6b7280; }",
) as demo:

    gr.Markdown(
        """
        # 🏦 Automated Transaction Ledger Engine
        Paste a raw bank feed line and watch it transform into a structured, categorised ledger entry — instantly, with no external API calls.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            raw_input = gr.Textbox(
                label="Raw Bank Feed String",
                placeholder='e.g.  25/03 UBER *TRIP SYDNEY AUD 42.50',
                lines=2,
            )
            with gr.Row():
                submit_btn = gr.Button("⚡ Process", variant="primary")
                clear_btn  = gr.Button("Clear")

            gr.Examples(
                examples=SAMPLE_FEEDS,
                inputs=raw_input,
                label="Sample bank feed lines — click to load",
            )

        with gr.Column(scale=1):
            gr.Markdown("### Extracted Fields")
            out_vendor     = gr.Textbox(label="Vendor")
            out_amount     = gr.Textbox(label="Amount")
            out_date       = gr.Textbox(label="Date")
            gr.Markdown("### Accounting Classification")
            out_category   = gr.Textbox(label="Category")
            out_confidence = gr.Textbox(label="Confidence")

    submit_btn.click(
        fn=process,
        inputs=raw_input,
        outputs=[out_vendor, out_amount, out_date, out_category, out_confidence],
    )
    clear_btn.click(
        fn=lambda: ("", "", "", "", "", ""),
        outputs=[raw_input, out_vendor, out_amount, out_date, out_category, out_confidence],
    )

    gr.Markdown(
        """
        ---
        **Architecture:** Deterministic regex for amounts/dates →
        Regex pre-filter to isolate merchant token →
        spaCy NER as enhancer →
        TF-IDF cosine similarity for category assignment.
        Zero external API calls · Sub-millisecond latency · No data leaves your machine.
        """
    )

if __name__ == "__main__":
    demo.launch(show_api=False)
