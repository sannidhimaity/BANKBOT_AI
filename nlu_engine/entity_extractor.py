"""
entity_extractor.py
Extracts structured entities (amounts, account numbers, names) from raw user text.
"""

import re


# ── Patterns ──────────────────────────────────────────────────────────────────

_AMOUNT_PATTERNS = [
    r"(?:rs\.?|inr|₹|\$)\s*(\d[\d,]*(?:\.\d{1,2})?)",
    r"(\d[\d,]*(?:\.\d{1,2})?)\s*(?:rs\.?|inr|rupees?|dollars?)",
    r"\b(\d{3,}(?:\.\d{1,2})?)\b",
]

_ACCOUNT_RE = re.compile(r"\b(\d{9,18})\b")

_RECIPIENT_RE = re.compile(
    r"\b(?:to|for|pay(?:ment to)?|send(?:\s+\w+)?\s+to|transfer(?:\s+\w+)?\s+to)\s+"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
)

_BANK_TYPES = ["savings", "current", "salary", "fixed deposit", "recurring", "demat", "joint", "zero balance"]
_LOAN_TYPES = ["personal", "home", "car", "education", "business", "gold", "vehicle"]
_CARD_TYPES = ["platinum", "gold", "silver", "rewards", "cashback", "travel"]


def extract_entities(text: str) -> dict:
    """
    Extract entities from user input.

    Returns a dict with keys: amount, account_number, recipient,
    account_type, loan_type, card_type (whichever are found).
    """
    entities: dict = {}

    # Amount
    for pattern in _AMOUNT_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            raw = m.group(1).replace(",", "")
            try:
                val = float(raw)
                if val > 0:
                    entities["amount"] = raw
                    break
            except ValueError:
                pass

    # Account number
    acct = _ACCOUNT_RE.search(text)
    if acct:
        entities["account_number"] = acct.group(1)

    # Recipient name
    recip = _RECIPIENT_RE.search(text)
    if recip:
        entities["recipient"] = recip.group(1)

    # Account type
    lower = text.lower()
    for atype in _BANK_TYPES:
        if atype in lower:
            entities["account_type"] = atype
            break

    # Loan type
    for ltype in _LOAN_TYPES:
        if ltype in lower:
            entities["loan_type"] = ltype
            break

    # Card type
    for ctype in _CARD_TYPES:
        if ctype in lower:
            entities["card_type"] = ctype
            break

    return entities
