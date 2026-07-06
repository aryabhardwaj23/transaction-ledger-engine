---
title: Transaction Ledger Engine
emoji: 🏦
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.40.0
python_version: '3.11'
app_file: app.py
pinned: false
---

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=28&duration=2800&pause=2000&color=10B981&center=true&vCenter=true&width=940&lines=Automated+Transaction+Ledger+Engine+%F0%9F%8F%A6;Upload+a+Bank+Statement+%E2%86%92+Financial+Dashboard;Raw+Bank+Feed+%E2%86%92+Structured+Ledger+Entry;No+External+APIs+%C2%B7+Sub-Millisecond+Latency" alt="Typing SVG" />
</div>

<div align="center">

## 👇 Try it live — no install required

### **[🚀 Open Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/arya2323/transaction-ledger-engine)**

*Upload a bank statement CSV or paste a single transaction — results in seconds*

---

[![Live Demo](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Demo-brightgreen?style=for-the-badge)](https://huggingface.co/spaces/arya2323/transaction-ledger-engine)
[![GitHub](https://img.shields.io/badge/GitHub-View%20Code-181717?style=for-the-badge&logo=github)](https://github.com/aryabhardwaj23/transaction-ledger-engine)

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-green.svg)
![spaCy](https://img.shields.io/badge/spaCy-NLP-blue.svg)
![scikit--learn](https://img.shields.io/badge/scikit--learn-TF--IDF-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)
![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75.svg)

</div>

---

## 🎯 What This Solves

Accounting SaaS products like MYOB, Xero, and QuickBooks all face the same hard problem: **raw bank feeds are unstructured noise**.

```
❌  Before:  "25/03 UBER *TRIP SYDNEY AUD 42.50"
✅  After:   Vendor: UBER  |  Amount: $42.50  |  Date: 25/03  |  Category: Travel & Transport
```

```
❌  Before:  "AMZN MKTP AU*2K4XR9 84.00"
✅  After:   Vendor: AMZN MKTP AU  |  Amount: $84.00  |  Category: Office Supplies
```

This engine normalises any raw bank string into a structured, categorised ledger entry — in under 5ms, with no external API calls and no financial data leaving the system.

---

## 🖥️ What the Live Demo Does

Two modes, one pipeline:

**⚡ Single Transaction** — paste any raw bank feed string, get back vendor, amount, date, category, and a confidence score with a visual progress bar.

**📊 Upload Bank Statement** — drag and drop a real CSV bank export (or use the built-in sample). The engine processes every row and renders a full financial dashboard:

| Dashboard Component | What it shows |
|---|---|
| **KPI row** | Total Income · Total Expenses · Net Cash Flow · Transaction count |
| **Spending donut chart** | Breakdown by ML-assigned category — interactive, hover for amounts |
| **Top vendors bar chart** | Ranked by total spend, animated on hover |
| **Debt & Finance tracker** | Automatically isolates loan repayments, BNPL, bank fees — shows % of total outflows |
| **Searchable ledger table** | Full transaction list, filterable by category or free-text search |

A **"Download Sample CSV"** button is built in — recruiters and reviewers can test the full dashboard in one click with no setup.

---

## 🏗️ System Architecture

```
 RAW BANK STRING
       │
       ▼
 ┌─────────────────────────────────────────────────────┐
 │  STAGE 1: PARSER                                    │
 │                                                     │
 │  Regex  ──▶  Amount   (deterministic, < 1ms)        │
 │  Regex  ──▶  Date     (5 AU/ISO format patterns)    │
 │  Regex  ──▶  Vendor token  (split on digit / * / /) │
 │  spaCy  ──▶  NER refinement on the clean token      │
 └─────────────────────────────────────────────────────┘
       │  { vendor, amount, date }
       ▼
 ┌─────────────────────────────────────────────────────┐
 │  STAGE 2: CATEGORISER                               │
 │                                                     │
 │  TF-IDF vectorise vendor string                     │
 │  Cosine similarity → nearest category centroid      │
 │  10 accounting categories  ·  Confidence score      │
 └─────────────────────────────────────────────────────┘
       │
       ▼
 { vendor, amount, date, category, confidence }
```

---

## 🧠 Key Engineering Decisions

### Why not just call an LLM API?

| | LLM API (GPT-4 / Claude) | This Engine |
|---|---|---|
| **Latency** | 200–800ms per call | < 5ms |
| **Cost** | ~$0.002 per transaction | $0.00 |
| **Data privacy** | Sends financial data to 3rd party | Nothing leaves your machine |
| **Scale** | Rate-limited | 500 req/batch, synchronous |
| **Explainability** | Black box | Every decision is traceable |

For financial data at scale, **deterministic + local** beats **powerful + expensive** every time.

### Why regex before NER?

Standard NER models (spaCy `en_core_web_sm`, `dslim/bert-base-NER`) are trained on news and web text — grammatical, mixed-case, structured sentences. Bank feeds are the opposite: `AMZN MKTP AU*2K4XR9`, `SQ *MARIO KART CAFE MELB`. Running NER directly on these strings produces near-zero ORG matches.

The fix: use regex to isolate the merchant substring *first*, removing digits, amounts, and special characters. NER then operates on a clean `"UBER"` or `"OFFICEWORKS"` — the domain it was trained for.

### Why TF-IDF over a trained classifier?

A trained classifier needs labelled data. TF-IDF cosine similarity against category seed vocabularies needs zero training data, is immediately interpretable (confidence = cosine score), and is extensible by simply adding new vendor keywords to a dictionary.

---

## 📊 Live Results

| Raw Bank String | Vendor | Amount | Date | Category |
|---|---|---|---|---|
| `25/03 UBER *TRIP SYDNEY AUD 42.50` | UBER | $42.50 | 25/03 | ✈️ Travel & Transport |
| `PAYPAL *SPOTIFY AU 10.99` | PAYPAL | $10.99 | — | 🏦 Banking & Finance |
| `01/07 OFFICEWORKS PTY LTD CLAYTON 67.40` | OFFICEWORKS CLAYTON | $67.40 | 01/07 | 🖊️ Office Supplies |
| `GOOGLE ADS 2025-07-01 250.00` | GOOGLE | $250.00 | 2025-07-01 | 📣 Advertising & Marketing |
| `28/06 NETFLIX.COM 22.99` | NETFLIX.COM | $22.99 | 28/06 | 🎬 Subscriptions |
| `TELSTRA BILL PAY 89.00` | TELSTRA | $89.00 | — | ⚡ Utilities & Bills |
| `CHEMIST WAREHOUSE 0421 34.95` | CHEMIST | $34.95 | — | 💊 Healthcare |

---

## 🚀 REST API

**Run locally:**
```bash
git clone https://github.com/aryabhardwaj23/transaction-ledger-engine.git
cd transaction-ledger-engine
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
# Interactive API docs → open http://localhost:8000/docs in your browser
```

**Single transaction:**
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

**Batch (up to 500):**
```bash
curl -X POST http://localhost:8000/process/batch \
  -H "Content-Type: application/json" \
  -d '[{"raw": "UBER *TRIP 42.50"}, {"raw": "NETFLIX.COM 22.99"}]'
```

---

## 📁 Project Structure

```
transaction-ledger-engine/
├── app.py                    # Streamlit dashboard (HF Spaces entry point)
├── .streamlit/config.toml    # Dark theme config
├── backend/
│   ├── parser.py             # Regex + spaCy parsing pipeline
│   ├── categoriser.py        # TF-IDF cosine similarity categoriser
│   ├── models.py             # Pydantic request/response models
│   └── main.py               # FastAPI app + all endpoints
├── frontend/
│   └── app.py                # Original single-transaction Gradio runner
└── requirements.txt
```

---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

</div>

---

## ✅ Skills Demonstrated

| Area | Detail |
|---|---|
| **NLP Pipeline Design** | Domain-aware parsing — why and when standard NER fails on bank data |
| **API Development** | REST API with FastAPI, Pydantic v2 models, batch endpoint (500/req) |
| **ML without training data** | TF-IDF + cosine similarity as a zero-shot classifier |
| **Data Engineering** | Auto-detect CSV column formats, pandas ingestion, PDF text extraction |
| **Data Visualisation** | Interactive Plotly charts, KPI metrics, filterable data tables |
| **Production thinking** | Latency, privacy, cost, and explainability trade-offs vs LLM APIs |
| **Deployment** | Live Streamlit dashboard on Hugging Face Spaces — one-click sample |

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=100&section=footer"/>

  **⭐ Star this repo if it helped you think differently about production NLP!**

  ![Visitor Count](https://komarev.com/ghpvc/?username=aryabhardwaj23-ledger&color=green&style=for-the-badge&label=VISITORS)
</div>
