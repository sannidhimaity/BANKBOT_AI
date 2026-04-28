"""
backend/responses.py
Maps (intent, entities) to natural-language replies.
"""

import random


_TEMPLATES: dict[str, list[str]] = {
    "check_balance": [
        "Your current {account_type} account balance is **₹{balance}**. Would you like a full statement?",
        "Balance as of today: **₹{balance}** available in your {account_type} account.",
        "Your account has **₹{balance}** available. Need a breakdown of recent credits/debits?",
    ],
    "transfer_money": [
        "Transfer of **₹{amount}** to **{recipient}** is initiated. Please verify via OTP sent to your registered mobile.",
        "Processing **₹{amount}** → **{recipient}**. Expected completion: 2–4 hours (NEFT) or instantly (IMPS).",
        "To confirm the transfer of **₹{amount}** to **{recipient}**, please authenticate with your MPIN.",
    ],
    "loan_inquiry": [
        "We offer **{loan_type} loans** up to ₹{loan_limit} at {rate}% p.a. Shall I check your eligibility?",
        "Our {loan_type} loan has a minimum tenure of 12 months and competitive interest rates starting at {rate}% p.a. Want to apply?",
        "For a {loan_type} loan, the EMI on ₹5L for 5 years at {rate}% p.a. would be approximately ₹{emi}/month.",
    ],
    "credit_card": [
        "Your **{card_type} Credit Card** application is easy — just Aadhaar + PAN. Approval in 24 hours!",
        "Current outstanding on your credit card: **₹{cc_due}**. Due date: {due_date}. Pay now to avoid interest.",
        "To block your lost credit card, call **1800-XXX-XXXX** or use Cards → Block Card in the app immediately.",
    ],
    "transaction_history": [
        "Here are your last 5 transactions:\n• ₹1,200 — Swiggy *(today)*\n• ₹8,500 — Rent *(yesterday)*\n• ₹450 — Big Bazaar *(2 days ago)*\n• ₹2,000 — ATM withdrawal *(3 days ago)*\n• ₹599 — Netflix *(5 days ago)*\n\nWant the full statement?",
        "Your monthly spend so far: **₹{spend}**. Top categories: Food (35%), Utilities (25%), Shopping (20%).",
    ],
    "open_account": [
        "Opening a **{account_type} account** needs: Aadhaar, PAN, passport photo & ₹500 initial deposit. Apply online in 5 minutes!",
        "For a {account_type} account, the minimum balance is **₹{min_bal}**. Documents: Aadhaar + PAN + address proof.",
        "Your {account_type} account can be opened 100% digitally — upload docs via our app and get your account number instantly!",
    ],
    "atm_services": [
        "Nearest ATM is **0.3 km away** at MG Road Branch. Open 24×7. Daily withdrawal limit: ₹25,000.",
        "To change your ATM PIN: Insert card → Select 'PIN Change' → Enter old PIN → Set new PIN. Or use Net Banking.",
        "Your debit card has been **blocked** as requested. A replacement card will arrive in 5–7 business days. Ref: BLK{ref}.",
    ],
    "customer_support": [
        "Connecting you to a support agent… Average wait: **3 minutes**. Toll-free: 1800-XXX-XXXX (24×7).",
        "Your complaint has been registered. Ticket **#TKT{ref}** raised. Our team will respond within 24 hours.",
        "I'm escalating this to our specialist team. You'll receive a callback within **30 minutes**. Reference: ESC{ref}.",
    ],
    "greet": [
        "Hello! 👋 Welcome to **BankBot AI**. I can help with balances, transfers, loans, cards, and more. What do you need?",
        "Hi there! I'm BankBot, your 24×7 banking assistant. How can I help you today?",
        "Namaste! 🙏 Welcome. Ask me anything about your accounts, transactions, or banking services.",
    ],
    "goodbye": [
        "Thank you for banking with us! Your session has been securely closed. Have a great day! 😊",
        "Goodbye! Stay safe. Remember, I'm here 24×7 whenever you need banking assistance.",
        "Take care! Your account is secure. Reach out anytime — we're always here for you.",
    ],
    "unknown": [
        "I didn't quite catch that. Could you rephrase? I can help with:\n• Balance inquiry\n• Fund transfers\n• Loans & credit cards\n• Transaction history\n• Account opening",
        "Hmm, I'm not sure about that. Try asking: *'Check my balance'* or *'Apply for a loan'*.",
        "I didn't understand that request. Please try rephrasing or type **help** for a list of things I can do.",
    ],
}

_LOAN_CONFIG = {
    "personal": ("25,00,000", "10.5", "10,624"),
    "home":     ("1,00,00,000", "8.4", "61,530"),
    "car":      ("15,00,000", "9.2", "31,175"),
    "education":("20,00,000", "9.0", "20,761"),
    "business": ("50,00,000", "12.0", "11,122"),
    "gold":     ("10,00,000", "8.8", "10,403"),
    "vehicle":  ("10,00,000", "9.5", "20,924"),
}

_ACCOUNT_MIN_BAL = {
    "savings":       "1,000",
    "current":       "10,000",
    "salary":        "0",
    "fixed deposit": "5,000",
    "recurring":     "500",
    "zero balance":  "0",
    "joint":         "1,000",
    "demat":         "0",
}


def generate_response(intent: str, entities: dict) -> str:
    """Generate a reply string for the given intent and extracted entities."""
    templates = _TEMPLATES.get(intent, _TEMPLATES["unknown"])
    template = random.choice(templates)

    # Simulated dynamic values
    balance     = f"{random.randint(10_000, 5_00_000):,}"
    spend       = f"{random.randint(5_000, 80_000):,}"
    cc_due      = f"{random.randint(500, 50_000):,}"
    due_date    = f"{random.randint(1, 28)} May 2026"
    ref         = str(random.randint(100_000, 999_999))

    # Entity resolution
    amount       = f"{entities.get('amount', 'the requested amount')}"
    recipient    = entities.get("recipient", "the recipient")
    account_type = entities.get("account_type", "savings")
    loan_type    = entities.get("loan_type", "personal")
    card_type    = entities.get("card_type", "Platinum")

    loan_limit, rate, emi = _LOAN_CONFIG.get(loan_type, ("25,00,000", "10.5", "10,624"))
    min_bal = _ACCOUNT_MIN_BAL.get(account_type, "1,000")

    return (
        template
        .replace("{balance}",      balance)
        .replace("{amount}",       amount)
        .replace("{recipient}",    recipient)
        .replace("{account_type}", account_type)
        .replace("{loan_type}",    loan_type)
        .replace("{loan_limit}",   loan_limit)
        .replace("{rate}",         rate)
        .replace("{emi}",          emi)
        .replace("{min_bal}",      min_bal)
        .replace("{card_type}",    card_type.title())
        .replace("{cc_due}",       cc_due)
        .replace("{due_date}",     due_date)
        .replace("{spend}",        spend)
        .replace("{ref}",          ref)
    )
