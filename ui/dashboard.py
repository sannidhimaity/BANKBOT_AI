
import streamlit as st

from database.db import SessionLocal
from database.models import Account, Transaction


def render_dashboard():

    user_id = st.session_state.get("user_id")

    if not st.session_state.get("authenticated") or not user_id:
        st.warning("Please log in to continue.")
        st.session_state["authenticated"] = False
        st.rerun()
        return

    db = SessionLocal()

    try:
        # Fetch only the logged-in user's accounts
        accounts = (
            db.query(Account)
            .filter(Account.user_id == user_id)
            .all()
        )

        st.title("🏦 BankBot AI")
        st.subheader(
            f"Welcome, {st.session_state.get('user_name', 'User')}!"
        )

        st.caption(
            f"Logged in as: {st.session_state.get('user_email', '')}"
        )

        st.divider()

        st.subheader("Your Banking Overview")

        if not accounts:
            st.info("No bank accounts are associated with your profile.")

        for account in accounts:

            balance = float(account.balance or 0)

            with st.container(border=True):

                st.markdown(
                    f"**{account.account_type.title()} Account**"
                )

                masked_number = "••••" + account.account_number[-4:]

                st.caption(f"Account Number: {masked_number}")

                st.metric(
                    "Available Balance",
                    f"₹{balance:,.2f}"
                )

        st.divider()

        st.subheader("Recent Transactions")

        if accounts:

            account_ids = [account.id for account in accounts]

            transactions = (
                db.query(Transaction)
                .filter(Transaction.account_id.in_(account_ids))
                .order_by(Transaction.created_at.desc())
                .limit(10)
                .all()
            )

            if transactions:

                for transaction in transactions:

                    amount = float(transaction.amount)

                    st.write(
                        f"**{transaction.transaction_type.title()}** "
                        f"— ₹{amount:,.2f}"
                    )

                    st.caption(
                        f"{transaction.description or 'Bank transaction'} "
                        f"| {transaction.created_at}"
                    )

            else:
                st.info("You don't have any transactions yet.")

        st.divider()

        st.subheader("Account Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Name**")
            st.write(st.session_state.get("user_name"))

        with col2:
            st.write("**Account Type**")
            st.write("Savings")

        st.divider()

        if st.button(
            "Logout",
            type="primary",
            use_container_width=True
        ):
            for key in [
                "authenticated",
                "user_id",
                "user_name",
                "user_email",
                "user_role"
            ]:
                st.session_state.pop(key, None)

            st.rerun()

    finally:
        db.close()
