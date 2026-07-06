import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Bank feeds use many date formats — cover the common ones
_MONTHS = "JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"
DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",                  # 2025-03-25  (ISO — must come first)
    r"\d{2}[/-]\d{2}[/-]\d{4}",            # 25/03/2025
    r"\d{2}[/-]\d{2}[/-]\d{2}",            # 25/03/25
    r"\d{2}[/-]\d{2}(?!\d)",               # 25/03  (year-less, AU bank feed)
    rf"\d{{2}}\s+(?:{_MONTHS})",            # 25 MAR  (month abbrev only)
]

# Noise words that follow a merchant name in bank feeds
_ENTITY_STOPWORDS = {"PTY", "LTD", "AU", "AUD", "PL", "INC", "LLC", "CO"}

# Characters that signal the end of a merchant name in a bank string
MERCHANT_BREAK = re.compile(r"[\*\d/\\]")

# Remove noise characters from extracted vendor text
NOISE_CHARS = re.compile(r"[^a-zA-Z0-9\s&\-.]")


def parse_transaction(raw_string: str) -> dict:
    """
    Parse a raw bank feed string into structured fields.

    Strategy:
      - Regex for deterministic fields (amount, date) — sub-millisecond, 100% reliable
      - Regex pre-filter to isolate the merchant token before NER — handles
        all-caps, asterisks, and abbreviations that break out-of-the-box NER
      - spaCy NER as an enhancer, not the primary extractor
    """
    # ── Amount ──────────────────────────────────────────────────────────────
    amounts = re.findall(r"\d{1,6}\.\d{2}", raw_string)
    amount = float(amounts[0]) if amounts else None

    # ── Date ─────────────────────────────────────────────────────────────────
    date = None
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, raw_string)
        if match:
            date = match.group()
            break

    # ── Vendor ───────────────────────────────────────────────────────────────
    # Strip leading date if present (some feeds start with DD/MM or DD/MM/YY)
    stripped = re.sub(r"^\d{2}[/-]\d{2}(?:[/-]\d{2,4})?\s*", "", raw_string).strip()

    # Everything before the first digit, asterisk, or slash is the merchant
    vendor_raw = MERCHANT_BREAK.split(stripped)[0].strip()
    vendor_raw = NOISE_CHARS.sub("", vendor_raw).strip()

    # Drop trailing legal/currency suffixes (PTY, LTD, AUD, AU ...)
    tokens = [t for t in vendor_raw.split() if t.upper() not in _ENTITY_STOPWORDS]
    vendor_raw = " ".join(tokens).strip()

    # spaCy NER as a refinement step on the cleaned token
    if vendor_raw:
        doc = nlp(vendor_raw)
        orgs = [e.text for e in doc.ents if e.label_ in ("ORG", "PERSON", "PRODUCT")]
        vendor = orgs[0] if orgs else vendor_raw
    else:
        vendor = "UNKNOWN"

    return {
        "vendor": vendor.strip() or "UNKNOWN",
        "amount": amount,
        "date": date,
        "raw": raw_string,
    }
