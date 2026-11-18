"""
app.py — BankBot AI  |  Streamlit entry point
Run: streamlit run app.py
"""
from backend.banking import generate_user_response
import sys
import os
import time
import json

# Ensure package root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from nlu_engine import (
    load_intents,
    save_intents,
    train_intent_model,
    predict_intent,
    reload_intent_model,
    load_intent_model,
    extract_entities,
)

from database.db import SessionLocal
from database.models import User

from ui.login import render_login
from ui.register import render_register

from backend import generate_response

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BankBot AI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# AUTHENTICATION GATE
# ==========================================

# Initialize appearance and authentication before rendering either auth page or dashboard.
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Keep the authentication screens visually consistent with the dashboard theme.
auth_dark = st.session_state.dark_mode
if auth_dark:
    auth_bg, auth_card, auth_text = "#0a0a12", "#13132a", "#e2e8f0"
    auth_muted, auth_border, auth_input = "#aab5c5", "#343454", "#1a1a35"
    auth_accent, auth_button_hover = "#7c3aed", "#6d28d9"
else:
    auth_bg, auth_card, auth_text = "#f5f6f8", "#ffffff", "#202a33"
    auth_muted, auth_border, auth_input = "#566574", "#d8dee7", "#ffffff"
    auth_accent, auth_button_hover = "#386b68", "#2d5855"

st.markdown(f"""
<style>
.stApp {{ background: {auth_bg} !important; }}
.main .block-container {{ max-width: 680px !important; padding: 2.2rem 1.5rem 3rem !important; }}
.auth-brand {{ text-align: center; padding: 18px 0 28px; }}
.auth-brand-title {{ color: {auth_text} !important; font-size: 2rem; font-weight: 800;
    letter-spacing: -.8px; line-height: 1.25; }}
.auth-brand-subtitle {{ color: {auth_muted} !important; font-size: .95rem; margin-top: 7px; }}
.auth-heading {{ text-align: center; padding: 8px 0 22px; }}
.auth-eyebrow {{ color: {auth_accent}; font-size: .7rem; font-weight: 800;
    letter-spacing: 1.8px; margin-bottom: 10px; }}
.auth-heading h1 {{ color: {auth_text} !important; font-size: 1.8rem;
    font-weight: 800; letter-spacing: -.7px; margin: 0 0 8px; }}
.auth-heading p {{ color: {auth_muted} !important; font-size: .95rem; margin: 0; }}
[data-testid="stForm"] {{ background: transparent; border: 0 !important; padding: 0 !important; }}
.stTextInput label, .stTextInput label p {{ color: {auth_text} !important; font-weight: 650 !important; }}
.stTextInput input {{ background: {auth_input} !important; color: {auth_text} !important;
    border: 1px solid {auth_border} !important; border-radius: 10px !important; min-height: 44px; }}
.stTextInput input::placeholder {{ color: {auth_muted} !important; opacity: 1; }}
.stFormSubmitButton button {{ background: {auth_accent} !important; color: #fff !important;
    border: 0 !important; border-radius: 10px !important; min-height: 46px;
    font-weight: 700 !important; }}
.stFormSubmitButton button:hover {{ background: {auth_button_hover} !important; }}
[data-testid="stRadio"] label, [data-testid="stRadio"] p {{ color: {auth_text} !important; }}
[data-testid="stAlert"] {{ border-radius: 10px; }}
@media (max-width: 640px) {{ .auth-brand {{ padding: 12px 0 22px; }} }}
</style>
""", unsafe_allow_html=True)


# Verify logged-in user against the database
if st.session_state["authenticated"]:

    db = SessionLocal()

    try:
        current_user = db.query(User).filter(
            User.id == st.session_state.get("user_id")
        ).first()

        if current_user:

            # Refresh identity and role from database
            st.session_state["user_name"] = current_user.name
            st.session_state["user_email"] = current_user.email
            st.session_state["user_role"] = current_user.role

        else:

            # Invalid or deleted user
            for key in [
                "authenticated",
                "user_id",
                "user_name",
                "user_email",
                "user_role"
            ]:
                st.session_state.pop(key, None)

            st.session_state["authenticated"] = False

    finally:
        db.close()


# Show login/register if user is not authenticated
if not st.session_state["authenticated"]:

    st.markdown(
        """
        <div class="auth-brand">
            <div class="auth-brand-title">🏦 BankBot AI</div>
            <div class="auth-brand-subtitle">Your intelligent banking assistant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    appearance_col, _ = st.columns([1, 3])
    with appearance_col:
        auth_mode_label = "☀️ Light appearance" if auth_dark else "🌙 Dark appearance"
        if st.button(auth_mode_label, key="auth_theme_toggle", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

    auth_page = st.radio(
        "Choose an option",
        ["Login", "Register"],
        horizontal=True,
        key="main_auth_page",
        label_visibility="collapsed",
    )

    if auth_page == "Login":
        render_login()
    else:
        render_register()

    st.stop()

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "intents"       not in st.session_state:
    st.session_state.intents = load_intents()
if "chat_history"  not in st.session_state:
    st.session_state.chat_history = []          # list of (role, text, meta)
if "model_trained" not in st.session_state:
    st.session_state.model_trained = load_intent_model() is not None
if "page"          not in st.session_state:
    st.session_state.page = "🏠  Home"

# ─────────────────────────────────────────────
#  THEME TOKENS
# ─────────────────────────────────────────────
dark = st.session_state.dark_mode

if dark:
    BG_APP        = "#0a0a12"
    BG_SIDEBAR    = "#0f0f1e"
    BG_CARD       = "#13132a"
    BG_INPUT      = "#1a1a35"
    BG_HOVER      = "#1e1e3a"
    BORDER        = "#2d2d5a"
    ACCENT        = "#7c3aed"       # purple-600
    ACCENT_LIGHT  = "#a78bfa"       # purple-400
    ACCENT_SOFT   = "#1e1040"       # purple-950 tint
    BTN_BG        = "#7c3aed"
    BTN_HOVER     = "#6d28d9"
    BTN_TEXT      = "#ffffff"
    TEXT_PRIMARY  = "#e2e8f0"
    TEXT_SECONDARY= "#94a3b8"
    TEXT_MUTED    = "#64748b"
    CHAT_USER_BG  = "#4c1d95"
    CHAT_USER_TXT = "#ede9fe"
    CHAT_BOT_BG   = "#1a1a35"
    CHAT_BOT_TXT  = "#e2e8f0"
    CHAT_BOT_BDR  = "#2d2d5a"
    STATUS_OK_BG  = "#14532d"
    STATUS_OK_TXT = "#86efac"
    STATUS_WN_BG  = "#78350f"
    STATUS_WN_TXT = "#fcd34d"
    BADGE_BG      = "#4c1d95"
    BADGE_TXT     = "#c4b5fd"
    EXPANDER_BG   = "#13132a"
    EXPANDER_BDR  = "#2d2d5a"
    SHADOW        = "rgba(0,0,0,0.6)"
    TAG_BG        = "#1e1040"
    TAG_TXT       = "#a78bfa"
    SIDEBAR_TXT   = "#c4b5fd"
    ICON_COLOR    = "#7c3aed"
    STAT_BG       = "#13132a"
    DIVIDER       = "#1e1e3a"
else:
    # Soft, warm light theme: lower glare with stronger text contrast.
    BG_APP        = "#f5f6f8"
    BG_SIDEBAR    = "#eef0f3"
    BG_CARD       = "#ffffff"
    BG_INPUT      = "#ffffff"
    BG_HOVER      = "#e9edf2"
    BORDER        = "#d8dee7"
    ACCENT        = "#386b68"       # muted teal
    ACCENT_LIGHT  = "#5b8985"
    ACCENT_SOFT   = "#e8f0ef"
    BTN_BG        = "#386b68"
    BTN_HOVER     = "#2d5855"
    BTN_TEXT      = "#ffffff"
    TEXT_PRIMARY  = "#202a33"
    TEXT_SECONDARY= "#46525e"
    TEXT_MUTED    = "#687583"
    CHAT_USER_BG  = "#386b68"
    CHAT_USER_TXT = "#ffffff"
    CHAT_BOT_BG   = "#ffffff"
    CHAT_BOT_TXT  = "#26323c"
    CHAT_BOT_BDR  = "#d8dee7"
    STATUS_OK_BG  = "#e7f3ed"
    STATUS_OK_TXT = "#245c42"
    STATUS_WN_BG  = "#f8f0df"
    STATUS_WN_TXT = "#76551c"
    BADGE_BG      = "#e6efed"
    BADGE_TXT     = "#2d5b57"
    EXPANDER_BG   = "#ffffff"
    EXPANDER_BDR  = "#d8dee7"
    SHADOW        = "rgba(31,45,56,0.07)"
    TAG_BG        = "#edf2f1"
    TAG_TXT       = "#315f5b"
    SIDEBAR_TXT   = "#34434e"
    ICON_COLOR    = "#386b68"
    STAT_BG       = "#ffffff"
    DIVIDER       = "#e1e5ea"

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

/* ── App background ── */
.stApp {{
    background-color: {BG_APP} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.main .block-container {{
    padding: 2rem 2.5rem !important;
    max-width: 1100px !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {BG_SIDEBAR} !important;
    border-right: 1px solid {BORDER} !important;
}}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {{
    color: {SIDEBAR_TXT} !important;
    font-weight: 500 !important;
}}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {SIDEBAR_TXT} !important;
}}

/* ── Headings ── */
h1 {{
    color: {TEXT_PRIMARY} !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.4px !important;
}}
h2 {{ color: {TEXT_PRIMARY} !important; font-weight: 600 !important; font-size: 1.3rem !important; }}
h3 {{ color: {TEXT_SECONDARY} !important; font-weight: 600 !important; font-size: 1.1rem !important; }}

/* ── Body text ── */
p, li, label, .stMarkdown {{
    color: {TEXT_SECONDARY} !important;
    font-size: 0.95rem !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: {BTN_BG} !important;
    color: {BTN_TEXT} !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.2px !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 8px {SHADOW} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
.stButton > button,
.stButton > button p,
.stButton > button span,
.stButton > button div {{
    color: #ffffff !important;
}}
.stFormSubmitButton > button,
.stFormSubmitButton > button p,
.stFormSubmitButton > button span {{
    color: #ffffff !important;
}}
.stButton > button:hover {{
    background: {BTN_HOVER} !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px {SHADOW} !important;
}}
.stButton > button:active {{
    transform: translateY(0px) !important;
}}

/* ── Danger button override (delete) ── */
.danger-btn .stButton > button {{
    background: {"#7f1d1d" if dark else "#fee2e2"} !important;
    color: {"#fca5a5" if dark else "#991b1b"} !important;
    box-shadow: none !important;
}}
.danger-btn .stButton > button:hover {{
    background: {"#991b1b" if dark else "#fecaca"} !important;
}}

/* ── Text inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background-color: {BG_INPUT} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT_PRIMARY} !important;
    font-size: 0.95rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 10px 14px !important;
    transition: border-color 0.18s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px {ACCENT}22 !important;
    outline: none !important;
}}
.stTextInput label, .stTextArea label {{
    color: {TEXT_SECONDARY} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.3px !important;
}}

/* ── Select box ── */
.stSelectbox > div > div {{
    background-color: {BG_INPUT} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT_PRIMARY} !important;
}}

/* ── Expander ── */
details summary {{
    background-color: {EXPANDER_BG} !important;
    border: 1px solid {EXPANDER_BDR} !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    color: {TEXT_PRIMARY} !important;
    font-weight: 600 !important;
    cursor: pointer !important;
}}
details[open] summary {{
    border-bottom-left-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
    border-bottom: none !important;
}}
details > div {{
    background-color: {EXPANDER_BG} !important;
    border: 1px solid {EXPANDER_BDR} !important;
    border-top: none !important;
    border-bottom-left-radius: 10px !important;
    border-bottom-right-radius: 10px !important;
    padding: 12px 16px !important;
}}

/* ── Divider ── */
hr {{
    border-color: {DIVIDER} !important;
    margin: 1.5rem 0 !important;
}}

/* ── Spinner ── */
.stSpinner > div > div {{
    border-top-color: {ACCENT} !important;
}}

/* ── Metric ── */
[data-testid="metric-container"] {{
    background: {STAT_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}}
[data-testid="metric-container"] label {{
    color: {TEXT_MUTED} !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {ACCENT} !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}}

/* ── Radio ── */
.stRadio > div {{
    gap: 6px !important;
}}
.stRadio label {{
    padding: 8px 12px !important;
    border-radius: 8px !important;
    transition: background 0.15s !important;
}}
.stRadio label:hover {{
    background: {BG_HOVER} !important;
}}

/* ── Info/success/warning banners ── */
.stAlert {{
    border-radius: 10px !important;
    border: none !important;
    font-size: 0.9rem !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {BG_APP}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {ACCENT}; }}

/* ── Chat bubbles ── */
.chat-wrapper {{ display: flex; flex-direction: column; gap: 10px; margin-top: 16px; }}
.chat-row-user {{ display: flex; justify-content: flex-end; }}
.chat-row-bot  {{ display: flex; justify-content: flex-start; }}

.bubble-user {{
    background: {CHAT_USER_BG};
    color: {CHAT_USER_TXT};
    padding: 12px 18px;
    border-radius: 20px 20px 4px 20px;
    max-width: 70%;
    font-size: 0.93rem;
    line-height: 1.6;
    box-shadow: 0 2px 8px {SHADOW};
}}
.bubble-bot {{
    background: {CHAT_BOT_BG};
    color: {CHAT_BOT_TXT};
    padding: 12px 18px;
    border-radius: 20px 20px 20px 4px;
    max-width: 75%;
    font-size: 0.93rem;
    line-height: 1.6;
    border: 1px solid {CHAT_BOT_BDR};
    box-shadow: 0 1px 4px {SHADOW};
}}
.chat-label-user {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    text-align: right;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
}}
.chat-label-bot {{
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
}}
.intent-badge {{
    display: inline-block;
    background: {BADGE_BG};
    color: {BADGE_TXT};
    font-size: 0.68rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
    margin-left: 8px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.3px;
    vertical-align: middle;
}}

/* ── Stat card ── */
.stat-card {{
    background: {STAT_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}}
.stat-card .stat-number {{
    font-size: 2rem;
    font-weight: 700;
    color: {ACCENT};
}}
.stat-card .stat-label {{
    font-size: 0.8rem;
    color: {TEXT_MUTED};
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-top: 4px;
}}

/* ── Feature card ── */
.feature-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 22px;
    height: 100%;
    transition: box-shadow 0.2s, transform 0.2s;
}}
.feature-card:hover {{
    box-shadow: 0 8px 24px {SHADOW};
    transform: translateY(-2px);
}}
.feature-card .icon {{
    font-size: 1.8rem;
    margin-bottom: 10px;
    display: block;
}}
.feature-card .title {{
    font-size: 1rem;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    margin-bottom: 6px;
}}
.feature-card .desc {{
    font-size: 0.87rem;
    color: {TEXT_SECONDARY};
    line-height: 1.6;
}}

/* ── Quick action pill ── */
.qa-pill {{
    display: inline-block;
    background: {TAG_BG};
    color: {TAG_TXT};
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.83rem;
    font-weight: 600;
    margin: 4px;
    border: 1px solid {BORDER};
    cursor: pointer;
    transition: background 0.15s;
}}
.qa-pill:hover {{
    background: {ACCENT_SOFT};
}}

/* ── Intent tag in trainer ── */
.intent-tag {{
    background: {TAG_BG};
    color: {TAG_TXT};
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid {BORDER};
}}

/* ── Page header ── */
.page-header {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
    box-shadow: 0 2px 12px {SHADOW};
}}
.page-header h1 {{
    margin: 0 !important;
    padding: 0 !important;
}}
.page-header p {{
    margin-top: 6px !important;
    font-size: 0.95rem !important;
    color: {TEXT_SECONDARY} !important;
}}

/* ── Input area wrapper ── */
.chat-input-area {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px {SHADOW};
}}

/* ── Score bar ── */
.score-bar-wrap {{ margin: 4px 0; }}
.score-label {{
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    color: {TEXT_SECONDARY};
    display: flex;
    justify-content: space-between;
    margin-bottom: 3px;
}}
.score-bar-bg {{
    background: {BORDER};
    border-radius: 4px;
    height: 7px;
    overflow: hidden;
}}
.score-bar-fill {{
    height: 100%;
    border-radius: 4px;
    background: {ACCENT};
}}

/* ── Mode toggle ── */
.mode-pill {{
    background: {TAG_BG};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 600;
    color: {TAG_TXT};
    cursor: pointer;
    display: inline-block;
}}

/* ── Status pill ── */
.status-ok {{
    background: {STATUS_OK_BG};
    color: {STATUS_OK_TXT} !important;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}}
.status-warn {{
    background: {STATUS_WN_BG};
    color: {STATUS_WN_TXT} !important;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}}

/* ── Accessible alert contrast ── */
[data-testid="stAlert"] p,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {{
    color: inherit !important;
    font-weight: 600 !important;
}}
[data-testid="stAlert"] {{ border-radius: 10px !important; }}
[data-testid="stMetric"] label, [data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: {TEXT_PRIMARY} !important;
}}

/* ── Refined page rhythm and responsive layout ── */
.main .block-container {{
    padding-top: 1.6rem !important;
    padding-bottom: 3rem !important;
}}
.page-header {{
    padding: 30px 34px !important;
    margin-bottom: 22px !important;
}}
.page-header h1 {{
    font-size: clamp(1.55rem, 2.4vw, 2rem) !important;
    line-height: 1.25 !important;
}}
.page-header p {{
    line-height: 1.65 !important;
    max-width: 720px;
}}
.feature-card {{
    min-height: 176px;
    padding: 22px !important;
    margin-bottom: 12px;
}}
.feature-card .title {{
    line-height: 1.4;
}}
.feature-card .desc {{
    line-height: 1.65;
}}
.chat-wrapper {{
    gap: 16px !important;
    padding: 8px 2px 14px;
}}
.bubble-user, .bubble-bot {{
    overflow-wrap: anywhere;
    line-height: 1.7 !important;
}}
.chat-input-area {{
    padding: 14px 16px !important;
    margin-top: 16px;
}}
.stMetric {{
    background: {STAT_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 12px 16px;
}}
.stForm {{
    border: 0 !important;
}}
.stFormSubmitButton > button {{
    min-height: 44px;
}}
.stTextInput > div > div > input::placeholder {{
    color: {TEXT_MUTED} !important;
    opacity: 1 !important;
}}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {{
    line-height: 1.65;
}}
@media (max-width: 900px) {{
    .main .block-container {{ padding-left: 1.1rem !important; padding-right: 1.1rem !important; }}
    .feature-card {{ min-height: 150px; }}
}}
@media (max-width: 640px) {{
    .page-header {{ padding: 22px !important; }}
    .bubble-user, .bubble-bot {{ max-width: 94% !important; }}
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def render_chat_message(sender: str, msg: str, meta: dict):
    if sender == "You":
        st.markdown(
            f'<div class="chat-row-user">'
            f'  <div>'
            f'    <div class="chat-label-user">You</div>'
            f'    <div class="bubble-user">{msg}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        badge = ""
        if meta.get("intent") and meta["intent"] != "unknown":
            pct = int(meta.get("confidence", 0) * 100)
            badge = f'<span class="intent-badge">{meta["intent"]} · {pct}%</span>'
        st.markdown(
            f'<div class="chat-row-bot">'
            f'  <div>'
            f'    <div class="chat-label-bot">BankBot {badge}</div>'
            f'    <div class="bubble-bot">{msg}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_confidence_bars(all_scores: dict):
    top5 = list(all_scores.items())[:5]
    bars_html = ""
    for intent, score in top5:
        pct = round(score * 100, 1)
        bars_html += f"""
        <div class="score-bar-wrap">
          <div class="score-label"><span>{intent}</span><span>{pct}%</span></div>
          <div class="score-bar-bg"><div class="score-bar-fill" style="width:{pct}%"></div></div>
        </div>"""
    st.markdown(bars_html, unsafe_allow_html=True)



# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:

    # Logo / title
    st.markdown(f"""
    <div style="padding: 16px 4px 8px 4px;">
        <div style="font-size:1.5rem; font-weight:800; color:{ACCENT}; letter-spacing:-0.5px;">
            🏦 BankBot AI
        </div>
        <div style="font-size:0.78rem; color:{TEXT_MUTED}; margin-top:2px; font-weight:500;">
            Intelligent Banking Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Logged-in user information
    st.markdown(
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:1px;color:{TEXT_MUTED};text-transform:uppercase;">Logged in as</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"**👤 {st.session_state.get('user_name', 'User')}**"
    )

    st.caption(
        st.session_state.get("user_email", "")
    )

    # Logout
    if st.button(
        "🚪 Logout",
        key="main_logout",
        use_container_width=True
    ):

        for key in [
            "authenticated",
            "user_id",
            "user_name",
            "user_email",
            "user_role",
            "chat_history",
            "page"
        ]:
            st.session_state.pop(key, None)

        st.rerun()

    st.markdown("---")

    # Navigation
    st.markdown(
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:1px;color:{TEXT_MUTED};text-transform:uppercase;margin-bottom:8px;">Navigation</div>',
        unsafe_allow_html=True
    )

    # Chatbot is now the main page, not a separate sidebar destination.
    nav_options = ["🏠  Home"]

    # Trainer available only to admins
    if st.session_state.get("user_role") == "admin":
        nav_options.append("🧠  Trainer")

    current_page = st.session_state.get(
        "page",
        "🏠  Home"
    )

    if current_page not in nav_options:
        current_page = "🏠  Home"

    page = st.radio(
        "nav",
        nav_options,
        index=nav_options.index(current_page),
        key="main_navigation",
        label_visibility="collapsed"
    )

    st.session_state.page = page

    st.markdown("---")

    # Status
    st.markdown(
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:1px;color:{TEXT_MUTED};text-transform:uppercase;margin-bottom:10px;">Status</div>',
        unsafe_allow_html=True
    )

    model_ok = st.session_state.model_trained

    st.markdown(
        f'<div class="{"status-ok" if model_ok else "status-warn"}">'
        f'{"✅ Model ready" if model_ok else "⚠️ Not trained"}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div style="margin-top:10px; font-size:0.83rem; color:{TEXT_SECONDARY};">
        <div style="margin-bottom:4px;">📚 Intents: <b style="color:{ACCENT};">{len(st.session_state.intents)}</b></div>
        <div>📝 Examples: <b style="color:{ACCENT};">{sum(len(i['examples']) for i in st.session_state.intents)}</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Dark / Light mode toggle
    st.markdown(
        f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:1px;color:{TEXT_MUTED};text-transform:uppercase;margin-bottom:8px;">Appearance</div>',
        unsafe_allow_html=True
    )

    mode_label = (
        "☀️ Switch to Light Mode"
        if dark else
        "🌙 Switch to Dark Mode"
    )

    if st.button(
        mode_label,
        key="toggle_mode",
        use_container_width=True
    ):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")

    # Version
    st.markdown(
        f'<div style="font-size:0.72rem; color:{TEXT_MUTED}; text-align:center;">v1.0.0 · BankBot AI</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
#  HOME PAGE — CHATBOT FIRST
# ─────────────────────────────────────────────

if page == "🏠  Home":
    st.markdown(f"""
    <div class="page-header">
        <h1>Welcome to BankBot AI 🏦</h1>
        <p>Your banking assistant, ready when you are. Ask about balances, transactions and banking services in natural language.</p>
    </div>
    """, unsafe_allow_html=True)

    # Model status
    if not st.session_state.model_trained:
        st.warning("⚠️ The NLU model has not been trained yet. An administrator can train it from Trainer.")
    else:
        st.markdown(
            '<span class="status-ok">✅ BankBot is ready — ask me anything!</span><br><br>',
            unsafe_allow_html=True
        )

    # Quick actions
    st.markdown(
        f'<div style="margin:22px 0 12px; font-size:0.76rem; color:{TEXT_MUTED}; font-weight:700; letter-spacing:1px;">START WITH A QUICK ACTION</div>',
        unsafe_allow_html=True
    )
    quick_actions = [
        "Check my balance",
        "Show transactions",
        "Apply for a loan",
        "Transfer money",
        "Block my card",
        "Nearest ATM",
    ]
    qa_cols = st.columns(3)
    for i, qa in enumerate(quick_actions):
        with qa_cols[i % 3]:
            if st.button(qa, key=f"home_qa_{i}", use_container_width=True):
                if not st.session_state.model_trained:
                    reply = "⚠️ The model has not been trained yet. Please contact an administrator."
                    meta = {}
                else:
                    result = predict_intent(qa)
                    entities = extract_entities(qa)
                    reply = generate_user_response(
                        result["intent"],
                        entities,
                        st.session_state["user_id"]
                    )
                    meta = result
                st.session_state.chat_history.append(("You", qa, {}))
                st.session_state.chat_history.append(("BankBot", reply, meta))
                st.rerun()

    st.markdown("---")

    # Conversation history
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-row-bot">
          <div>
            <div class="chat-label-bot">BankBot</div>
            <div class="bubble-bot">
              👋 Hi! I'm BankBot AI. I can help you with:<br>
              • Account balance &amp; statements<br>
              • Fund transfers<br>
              • Loans &amp; credit cards<br>
              • ATM services &amp; more<br><br>
              What can I help you with today?
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        for sender, msg, meta in st.session_state.chat_history:
            render_chat_message(sender, msg, meta)
        st.markdown("</div>", unsafe_allow_html=True)

    # Message composer — clear_on_submit empties the field after Send/Enter.
    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        inp_col, btn_col = st.columns([5, 1])
        with inp_col:
            user_input = st.text_input(
                "Message",
                placeholder="Type your banking query… e.g. 'What is my balance?'",
                key="chat_input",
                label_visibility="collapsed",
            )
        with btn_col:
            send = st.form_submit_button("Send ➤", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if send and user_input.strip():
        if not st.session_state.model_trained:
            reply = "⚠️ The NLU model has not been trained yet. Please contact an administrator."
            meta = {}
        else:
            with st.spinner("Thinking…"):
                result = predict_intent(user_input)
                entities = extract_entities(user_input)
                reply = generate_user_response(
                    result["intent"],
                    entities,
                    st.session_state["user_id"]
                )
                meta = result
                time.sleep(0.3)

        st.session_state.chat_history.append(("You", user_input, {}))
        st.session_state.chat_history.append(("BankBot", reply, meta))
        st.rerun()

    # Prediction details
    last_bot = [
        (message, meta)
        for sender, message, meta in st.session_state.chat_history
        if sender == "BankBot" and meta
    ]
    if last_bot:
        with st.expander("🔍 Last prediction details", expanded=False):
            _, last_meta = last_bot[-1]
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Intent:** `{last_meta.get('intent', '—')}`")
                st.markdown(f"**Confidence:** `{round(last_meta.get('confidence', 0) * 100, 1)}%`")
            with c2:
                if last_meta.get("all_scores"):
                    render_confidence_bars(last_meta["all_scores"])

    if st.session_state.chat_history:
        if st.button("🗑️ Clear conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    # Keep the feature overview below the working chatbot.
    st.markdown("---")
    total_examples = sum(len(i["examples"]) for i in st.session_state.intents)
    st.markdown(f"""
    <div style="margin:8px 0 18px;">
      <div style="font-size:0.75rem; font-weight:700; letter-spacing:1px; color:{TEXT_MUTED}; margin-bottom:6px;">EXPLORE THE ASSISTANT</div>
      <h2 style="color:{TEXT_PRIMARY}; margin:0;">What can BankBot help you with?</h2>
      <p style="color:{TEXT_SECONDARY}; margin-top:6px;">Explore the services and capabilities available in this prototype.</p>
    </div>
    """, unsafe_allow_html=True)

    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.metric("Supported intents", len(st.session_state.intents))
    with stats_col2:
        st.metric("Training examples", total_examples)
    with stats_col3:
        st.metric("Messages in this session", len(st.session_state.chat_history) // 2)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    features = [
        ("💰", "Balance Inquiry", "Check your account balance and get detailed breakdowns instantly."),
        ("💸", "Fund Transfers", "Explore the transfer conversation flow. Actual bank-network transfers are not connected."),
        ("🏠", "Loan Services", "Explore personal, home, car, and education loan options."),
        ("💳", "Credit Cards", "Explore credit-card queries and common card-service guidance."),
        ("📊", "Transactions", "Review transaction-history functionality for your linked demo account."),
        ("🏦", "Account Opening", "Learn about savings, current and fixed-deposit account options."),
        ("🏧", "ATM Services", "Get general ATM and debit-card service guidance."),
        ("🎧", "Support", "Get guidance for common banking support questions."),
    ]
    feature_cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(features):
        with feature_cols[i % 4]:
            st.markdown(f"""
            <div class="feature-card">
                <span class="icon">{icon}</span>
                <div class="title">{title}</div>
                <div class="desc">{desc}</div>
            </div><br>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TRAINER PAGE
# ─────────────────────────────────────────────
elif page == "🧠  Trainer":
    if st.session_state.get("user_role") != "admin":
        st.error("You are not authorized to access the Trainer.")
        st.session_state.page = "🏠  Home"
        st.stop()

    st.markdown(f"""
    <div class="page-header">
        <h1>🧠 NLU Trainer</h1>
        <p>Manage intents, add training examples, and train the intent classification model.</p>
    </div>
    """, unsafe_allow_html=True)

    intents = st.session_state.intents

    # ── Stats ──
    total_ex = sum(len(i["examples"]) for i in intents)
    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("Total Intents", len(intents))
    with s2:
        st.metric("Total Examples", total_ex)
    with s3:
        avg = round(total_ex / len(intents), 1) if intents else 0
        st.metric("Avg Examples / Intent", avg)

    st.markdown("---")

    # ── Train model ──
    st.markdown(f'<h2 style="color:{TEXT_PRIMARY};">⚙️ Train Model</h2>', unsafe_allow_html=True)
    t1, t2 = st.columns([3, 1])
    with t1:
        st.markdown(f"""
        <div style="background:{BG_CARD}; border:1px solid {BORDER}; border-radius:10px; padding:14px 18px; font-size:0.88rem; color:{TEXT_SECONDARY};">
            Training uses <b>TF-IDF + Logistic Regression</b> with bigrams and cross-validation accuracy reporting.
            Retrain whenever you add or edit intents.
        </div>
        """, unsafe_allow_html=True)
    with t2:
        if st.button("🚀 Train Model", key="train_btn", use_container_width=True):
            with st.spinner("Training NLU model…"):
                result = train_intent_model(intents)
                reload_intent_model()
            if result["success"]:
                st.session_state.model_trained = True
                st.success(f"✅ {result['message']}")
            else:
                st.error(f"❌ {result['message']}")

    st.markdown("---")

    # ── Current intents ──
    st.markdown(f'<h2 style="color:{TEXT_PRIMARY};">📚 Intent Library</h2>', unsafe_allow_html=True)

    search_term = st.text_input("🔍 Filter intents", placeholder="Search by intent name…", key="intent_search")

    filtered = [i for i in intents if search_term.lower() in i["name"].lower()] if search_term else intents

    if not filtered:
        st.info("No intents match your search.")
    else:
        for idx, intent in enumerate(intents):  # iterate original for index-safe deletion
            if search_term and search_term.lower() not in intent["name"].lower():
                continue

            with st.expander(
                f"🏷️  {intent['name']}  ·  {len(intent['examples'])} examples",
                expanded=False,
            ):
                # Examples list
                ex_col, del_col = st.columns([4, 1])
                with ex_col:
                    for ex in intent["examples"]:
                        st.markdown(
                            f'<div style="padding:5px 0; font-size:0.87rem; color:{TEXT_SECONDARY}; border-bottom:1px solid {DIVIDER};">• {ex}</div>',
                            unsafe_allow_html=True,
                        )

                with del_col:
                    # Add example
                    new_ex = st.text_input("Add example", key=f"addex_{idx}", label_visibility="collapsed",
                                           placeholder="New example…")
                    if st.button("➕ Add", key=f"add_ex_{idx}"):
                        if new_ex.strip():
                            st.session_state.intents[idx]["examples"].append(new_ex.strip())
                            save_intents(st.session_state.intents)
                            st.success("Example added!")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                # Delete intent
                st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                if st.button(f"🗑️ Delete intent '{intent['name']}'", key=f"del_{idx}"):
                    st.session_state.intents.pop(idx)
                    save_intents(st.session_state.intents)
                    st.warning(f"Deleted intent: **{intent['name']}**")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Add new intent ──
    st.markdown(f'<h2 style="color:{TEXT_PRIMARY};">➕ Add New Intent</h2>', unsafe_allow_html=True)

    with st.form("add_intent_form", clear_on_submit=True):
        f1, f2 = st.columns([2, 3])
        with f1:
            new_name = st.text_input("Intent name *", placeholder="e.g. check_balance")
        with f2:
            new_examples = st.text_area(
                "Training examples * (one per line)",
                placeholder="What is my balance?\nShow me my account balance\nHow much money do I have?",
                height=120,
            )
        submitted = st.form_submit_button("✅ Add Intent", use_container_width=False)

        if submitted:
            name_clean = new_name.strip().lower().replace(" ", "_")
            if not name_clean:
                st.error("Intent name cannot be empty.")
            elif any(i["name"] == name_clean for i in st.session_state.intents):
                st.error(f"Intent `{name_clean}` already exists. Delete it first to replace.")
            else:
                examples = [e.strip() for e in new_examples.split("\n") if e.strip()]
                if not examples:
                    st.error("Please provide at least one training example.")
                elif len(examples) < 3:
                    st.warning(f"Intent added, but consider adding more examples (you have {len(examples)} — 5+ recommended).")
                    st.session_state.intents.append({"name": name_clean, "examples": examples})
                    save_intents(st.session_state.intents)
                    st.rerun()
                else:
                    st.session_state.intents.append({"name": name_clean, "examples": examples})
                    save_intents(st.session_state.intents)
                    st.success(f"✅ Intent `{name_clean}` added with {len(examples)} examples. Retrain the model to use it.")
                    st.rerun()

    st.markdown("---")

    # ── Quick test ──
    st.markdown(f'<h2 style="color:{TEXT_PRIMARY};">🧪 Quick Test</h2>', unsafe_allow_html=True)

    test_col, test_btn_col = st.columns([4, 1])
    with test_col:
        test_query = st.text_input("Test sentence", placeholder="e.g. I want to transfer 500 to Priya", key="test_query")
    with test_btn_col:
        test_btn = st.button("Test ▶", key="test_btn", use_container_width=True)

    if test_btn and test_query.strip():
        if not st.session_state.model_trained:
            st.warning("Train the model first!")
        else:
            result   = predict_intent(test_query)
            entities = extract_entities(test_query)

            tr1, tr2, tr3 = st.columns(3)
            with tr1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{result['intent']}</div>
                    <div class="stat-label">Predicted intent</div>
                </div>
                """, unsafe_allow_html=True)
            with tr2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{round(result['confidence']*100,1)}%</div>
                    <div class="stat-label">Confidence</div>
                </div>
                """, unsafe_allow_html=True)
            with tr3:
                ent_str = ", ".join(f"{k}: {v}" for k, v in entities.items()) if entities else "none"
                st.markdown(f"""
                <div class="stat-card" style="text-align:left;">
                    <div style="font-size:0.75rem; color:{TEXT_MUTED}; font-weight:700; letter-spacing:0.5px; text-transform:uppercase; margin-bottom:8px;">Entities</div>
                    <div style="font-size:0.85rem; font-family:'JetBrains Mono',monospace; color:{ACCENT};">{ent_str}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**All scores:**")
            render_confidence_bars(result["all_scores"])

            st.markdown(f"<br>**Generated response:**", unsafe_allow_html=True)
            response = generate_response(result["intent"], entities)
            st.markdown(f"""
            <div class="bubble-bot" style="max-width:100%; display:block;">
                {response}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  REQUIREMENTS.TXT  (written alongside app)
# ─────────────────────────────────────────────
_req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
if not os.path.exists(_req_path):
    with open(_req_path, "w") as f:
        f.write("streamlit>=1.32.0\nscikit-learn>=1.3.0\nnumpy>=1.24.0\n")
