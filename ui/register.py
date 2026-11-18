import streamlit as st

from database.db import SessionLocal
from auth.authentication import register_user


def render_register():
    """Render the BankBot AI account-creation form."""
    st.markdown(
        """
        <div class="auth-heading">
            <div class="auth-eyebrow">GET STARTED WITH BANKBOT</div>
            <h1>Create your account</h1>
            <p>A smarter way to explore your banking services.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("registration_form", clear_on_submit=False):
        name = st.text_input(
            "Full name",
            placeholder="Enter your full name",
            autocomplete="name",
        )
        email = st.text_input(
            "Email address",
            placeholder="name@example.com",
            autocomplete="email",
        )
        password = st.text_input(
            "Create password",
            type="password",
            placeholder="Choose a strong password",
            autocomplete="new-password",
        )
        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Re-enter your password",
            autocomplete="new-password",
        )
        submitted = st.form_submit_button(
            "Create account",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        clean_name = name.strip()
        clean_email = email.strip()
        if not clean_name or not clean_email or not password or not confirm_password:
            st.error("Please complete all fields.")
        elif password != confirm_password:
            st.error("The passwords do not match. Please try again.")
        else:
            db = SessionLocal()
            try:
                success, message = register_user(
                    db,
                    clean_name,
                    clean_email,
                    password,
                )
                if success:
                    st.success(message)
                    st.info("Your account is ready. Select Login above to sign in.")
                else:
                    st.error(message)
            finally:
                db.close()
