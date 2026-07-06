<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=28&duration=2800&pause=2000&color=10B981&center=true&vCenter=true&width=940&lines=Automated+Transaction+Ledger+Engine+%F0%9F%8F%A6;Raw+Bank+Feed+%E2%86%92+Structured+Ledger+Entry;No+External+APIs+%C2%B7+Sub-Millisecond+Latency" alt="Typing SVG" />
</div>

<div align="center">

[![Live Demo](https://img.shields.io/badge/%F0%9F%A4%97%20Live%20Demo-Hugging%20Face%20Spaces-blue)](https://huggingface.co/spaces/arya2323/transaction-ledger-engine)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green.svg)
![spaCy](https://img.shields.io/badge/spaCy-3.7+-blue.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-orange.svg)
![Gradio](https://img.shields.io/badge/Gradio-4.36+-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

**🚀 [Try the live demo](https://huggingface.co/spaces/arya2323/transaction-ledger-engine)** — no install required, works in your browser.

Turns messy, unstructured bank feed strings into clean, categorised accounting entries — entirely locally, with zero external API calls.

</div>

---

## 🏦 The Problem

One of the toughest challenges in fintech/SaaS accounting is **transaction normalisation**. Raw bank feeds look like this:

```
25/03 UBER *TRIP SYDNEY AUD 42.50
AMZN MKTP AU*2K4XR9 84.00
PAYPAL *SPOTIFY AU 10.99
SQ *MARIO KART CAFE MELB 26.50
```

Out-of-the-box LLMs and general-purpose NER models (spaCy, BERT) **fail on this data** — they were trained on grammatical text with proper casing and punctuation. Bank strings have none of that: all-caps, asterisks, truncated abbreviations, no sentence structure.

This engine solves it with a pragmatic, two-stage pipeline designed for production constraints.

---

## ⚙️ Architecture

```
Raw Bank String
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1 — PARSER  (backend/parser.py)                      │
│                                                             │
│  ① Regex for Amount  →  deterministic, 100% reliable       │
│  ② Regex for Date    →  5 format patterns, ISO-first order  │
│  ③ Regex pre-filter  →  isolate merchant token              │
│     (split on first digit / asterisk / slash)               │
│  ④ spaCy NER         →  enhancer on the clean token only    │
└─────────────────────────────────────────────────────────────┘
      │
      ▼  { vendor, amount, date }
      │
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2 — CATEGORISER  (backend/categoriser.py)            │
│                                                             │
│  TF-IDF vectorisation of vendor string                      │
│  Cosine similarity → nearest category centroid              │
│  10 categories, seeded with domain-specific vocabulary      │
│  Confidence score returned alongside category               │
└─────────────────────────────────────────────────────────────┘
      │
      ▼
{ vendor, amount, date, category, confidence }
```

**Why not an LLM API?**
Calling GPT-4 or Claude to extract "UBER" from a 40-character string introduces 200–800ms API latency, per-token cost, and — critically for financial data — **third-party data exposure**. The regex + spaCy + TF-IDF stack runs in **< 5ms** locally with zero privacy risk.

---

## 📊 Sample Output

| Raw Input | Vendor | Amount | Date | Category | Confidence |
|---|---|---|---|---|---|
| `25/03 UBER *TRIP SYDNEY AUD 42.50` | UBER | $42.50 | 25/03 | Travel & Transport | 12.4% |
| `PAYPAL *SPOTIFY AU 10.99` | PAYPAL | $10.99 | — | Banking & Finance | 14.3% |
| `01/07 OFFICEWORKS PTY LTD CLAYTON 67.40` | OFFICEWORKS CLAYTON | $67.40 | 01/07 | Office Supplies | 27.7% |
| `GOOGLE ADS 2025-07-01 250.00` | GOOGLE | $250.00 | 2025-07-01 | Advertising & Marketing | 14.7% |
| `28/06 NETFLIX.COM 22.99` | NETFLIX.COM | $22.99 | 28/06 | Subscriptions & Entertainment | 16.5% |
| `Commonwealth Bank Fee 25/06/25 12.00` | Commonwealth Bank Fee | $12.00 | 25/06/25 | Banking & Finance | 30.5% |

---

## 🚀 Quick Start

```bash
git clone https://github.com/aryabhardwaj23/transaction-ledger-engine.git
cd transaction-ledger-engine

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**Run the Gradio demo:**
```bash
python frontend/app.py
```

**Run the FastAPI backend:**
```bash
uvicorn backend.main:app --reload
# API docs at http://localhost:8000/docs
```

---

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/process` | Full pipeline: raw string → ledger entry |
| `POST` | `/process/batch` | Process up to 500 entries in one request |
| `POST` | `/parse` | Parser only: extract vendor, amount, date |
| `POST` | `/categorise` | Categoriser only: assign category to parsed vendor |

**Example:**
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"raw": "25/03 UBER *TRIP SYDNEY AUD 42.50"}'
```
```json
{
  "vendor": "UBER",
  "amount": 42.5,
  "date": "25/03",
  "category": "Travel & Transport",
  "confidence": 0.124,
  "raw": "25/03 UBER *TRIP SYDNEY AUD 42.50"
}
```

---

## 📁 Project Structure

```
transaction-ledger-engine/
├── backend/
│   ├── parser.py        # Regex + spaCy parsing pipeline
│   ├── categoriser.py   # TF-IDF cosine similarity categoriser
│   ├── models.py        # Pydantic request/response models
│   └── main.py          # FastAPI app + endpoints
├── frontend/
│   └── app.py           # Gradio demo UI
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-FF6F00?style=for-the-badge&logo=gradio&logoColor=white)

</div>

---

## 📈 Extending the Categoriser

The `CATEGORY_SEEDS` dictionary in `categoriser.py` drives classification. Add new vendor keywords to improve accuracy for your domain:

```python
CATEGORY_SEEDS["Software & SaaS"].extend(["linear", "retool", "segment", "mixpanel"])
```

No retraining required — the TF-IDF centroids are rebuilt at startup.

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=100&section=footer"/>

  **⭐ Star this repo if it helped you understand production-grade NLP pipelines!**

  ![Visitor Count](https://komarev.com/ghpvc/?username=aryabhardwaj23-ledger&color=green&style=for-the-badge&label=VISITORS)
</div>
