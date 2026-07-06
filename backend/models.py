from pydantic import BaseModel
from typing import Optional


class TransactionInput(BaseModel):
    raw: str


class ParsedTransaction(BaseModel):
    vendor: str
    amount: Optional[float]
    date: Optional[str]
    raw: str


class LedgerEntry(BaseModel):
    vendor: str
    amount: Optional[float]
    date: Optional[str]
    category: str
    confidence: float
    raw: str
