import streamlit as st

from database.db import SessionLocal
from auth.authentication import authenticate_user


def render_login():
    """Render the BankBot AI sign-in form."""
    st.markdown(
        """
        <div class="auth-heading">
            <div class="auth-eyebrow">SECURE DIGITAL BANKING</div>
            <h1>Welcome back</h1>
            <p>Sign in to continue to your BankBot dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email address",
            placeholder="name@example.com",
            autocomplete="email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            autocomplete="current-password",
        )
        submitted = st.form_submit_button(
            "Sign in",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        if not email.strip() or not password:
            st.error("Please enter your email address and password.")
            return

        db = SessionLocal()
        try:
            user = authenticate_user(db, email.strip(), password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["user_id"] = user.id
                st.session_state["user_name"] = user.name
                st.session_state["user_email"] = user.email
                st.session_state["user_role"] = user.role
                st.success("Login successful. Opening your dashboard…")
                st.rerun()
            else:
                st.error("Invalid email or password. Please try again.")
        finally:
            db.close()
