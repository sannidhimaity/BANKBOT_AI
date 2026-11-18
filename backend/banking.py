
"""
backend/banking.py

Database-connected banking operations for BankBot AI.
All account queries are restricted to the authenticated user.
"""

from database.db import SessionLocal
from database.models import Account, Transaction
from sqlalchemy import desc


def get_user_accounts(db, user_id):
    """Retrieve only the accounts belonging to this user."""

    return (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .order_by(Account.id)
        .all()
    )


def get_user_transactions(db, user_id, limit=5):
    """Retrieve recent transactions belonging to this user."""

    return (
        db.query(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.user_id == user_id)
        .order_by(desc(Transaction.created_at))
        .limit(limit)
        .all()
    )


def get_balance_response(db, user_id):
    """Generate a balance response using actual database values."""

    accounts = get_user_accounts(db, user_id)

    if not accounts:
        return "You don't have any bank accounts registered yet."

    total_balance = sum(
        (account.balance for account in accounts),
        start=0
    )

    response = "Here are your account details:\n\n"

    for account in accounts:
        masked_number = "XXXX" + account.account_number[-4:]

        response += (
            f"**{account.account_type.title()} Account**\n"
            f"Account Number: {masked_number}\n"
            f"Available Balance: ₹{account.balance:,.2f}\n\n"
        )

    if len(accounts) > 1:
        response += f"**Total Balance: ₹{total_balance:,.2f}**"

    return response


def get_transaction_response(db, user_id):
    """Generate transaction history from actual database records."""

    transactions = get_user_transactions(db, user_id)

    if not transactions:
        return "You don't have any transactions yet."

    response = "**Here are your 5 most recent transactions:**\n\n"

    for transaction in transactions:

        amount = float(transaction.amount)

        date = (
            transaction.created_at.strftime("%d %b %Y, %I:%M %p")
            if transaction.created_at
            else "Date unavailable"
        )

        description = (
            transaction.description or "Banking transaction"
        )

        response += (
            f"• **{transaction.transaction_type.title()}**"
            f" — ₹{amount:,.2f}\n"
            f"  {description}\n"
            f"  {date}\n\n"
        )

    return response


def generate_user_response(intent, entities, user_id):
    """
    Generate a response using the authenticated user's database records.

    Database-backed intents:
    - check_balance
    - transaction_history

    Other intents continue using the existing NLU response engine.
    """

    db = SessionLocal()

    try:

        if intent in ("check_balance", "balance_inquiry"):

            return get_balance_response(db, user_id)

        elif intent in (
            "transaction_history",
            "show_transactions",
            "check_transactions"
        ):

            return get_transaction_response(db, user_id)

        # Preserve existing responses for other intents.
        from backend.responses import generate_response

        return generate_response(intent, entities)

    except Exception as error:

        print(f"Banking database error: {error}")

        return (
            "Sorry, I couldn't retrieve your banking information "
            "right now. Please try again."
        )

    finally:
        db.close()
