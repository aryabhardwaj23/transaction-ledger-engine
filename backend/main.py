from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import TransactionInput, ParsedTransaction, LedgerEntry
from .parser import parse_transaction
from .categoriser import categoriser

app = FastAPI(
    title="Transaction Ledger Engine",
    description=(
        "Parses raw bank feed strings into structured ledger entries. "
        "Uses deterministic regex for financial fields and a TF-IDF cosine "
        "similarity pipeline for accounting category assignment — "
        "no external API calls, sub-millisecond latency."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse", response_model=ParsedTransaction)
def parse(body: TransactionInput):
    """Extract vendor, amount, and date from a raw bank feed string."""
    if not body.raw.strip():
        raise HTTPException(status_code=400, detail="Input string is empty.")
    return parse_transaction(body.raw)


@app.post("/categorise")
def categorise(body: ParsedTransaction):
    """Assign an accounting category to an already-parsed transaction."""
    result = categoriser.categorise(body.vendor)
    return {**body.model_dump(), **result}


@app.post("/process", response_model=LedgerEntry)
def process(body: TransactionInput):
    """Full pipeline: raw string → parsed fields → categorised ledger entry."""
    if not body.raw.strip():
        raise HTTPException(status_code=400, detail="Input string is empty.")

    parsed = parse_transaction(body.raw)
    cat = categoriser.categorise(parsed["vendor"])

    return LedgerEntry(
        vendor=parsed["vendor"],
        amount=parsed["amount"],
        date=parsed["date"],
        category=cat["category"],
        confidence=cat["confidence"],
        raw=parsed["raw"],
    )


@app.post("/process/batch", response_model=list[LedgerEntry])
def process_batch(body: list[TransactionInput]):
    """Process multiple bank feed lines in one request."""
    if len(body) > 500:
        raise HTTPException(status_code=400, detail="Batch limit is 500 entries.")
    results = []
    for item in body:
        parsed = parse_transaction(item.raw)
        cat = categoriser.categorise(parsed["vendor"])
        results.append(LedgerEntry(
            vendor=parsed["vendor"],
            amount=parsed["amount"],
            date=parsed["date"],
            category=cat["category"],
            confidence=cat["confidence"],
            raw=parsed["raw"],
        ))
    return results
