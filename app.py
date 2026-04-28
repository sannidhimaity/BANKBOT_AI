"""
app.py — BankBot AI  |  Streamlit entry point
Run: streamlit run app.py
"""

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

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "intents"       not in st.session_state:
    st.session_state.intents = load_intents()
if "chat_history"  not in st.session_state:
    st.session_state.chat_history = []          # list of (role, text, meta)
if "model_trained" not in st.session_state:
    st.session_state.model_trained = load_intent_model() is not None
if "dark_mode"     not in st.session_state:
    st.session_state.dark_mode = False
if "page"          not in st.session_state:
    st.session_state.page = "Home"

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
    BG_APP        = "#f0f4ff"
    BG_SIDEBAR    = "#e8efff"
    BG_CARD       = "#ffffff"
    BG_INPUT      = "#ffffff"
    BG_HOVER      = "#f0f4ff"
    BORDER        = "#bfdbfe"
    ACCENT        = "#2563eb"       # blue-600
    ACCENT_LIGHT  = "#60a5fa"       # blue-400
    ACCENT_SOFT   = "#eff6ff"       # blue-50
    BTN_BG        = "#2563eb"
    BTN_HOVER     = "#1d4ed8"
    BTN_TEXT      = "#ffffff"
    TEXT_PRIMARY  = "#1e293b"
    TEXT_SECONDARY= "#475569"
    TEXT_MUTED    = "#94a3b8"
    CHAT_USER_BG  = "#2563eb"
    CHAT_USER_TXT = "#ffffff"
    CHAT_BOT_BG   = "#ffffff"
    CHAT_BOT_TXT  = "#1e293b"
    CHAT_BOT_BDR  = "#bfdbfe"
    STATUS_OK_BG  = "#f0fdf4"
    STATUS_OK_TXT = "#166534"
    STATUS_WN_BG  = "#fffbeb"
    STATUS_WN_TXT = "#92400e"
    BADGE_BG      = "#dbeafe"
    BADGE_TXT     = "#1e40af"
    EXPANDER_BG   = "#f8faff"
    EXPANDER_BDR  = "#bfdbfe"
    SHADOW        = "rgba(37,99,235,0.10)"
    TAG_BG        = "#eff6ff"
    TAG_TXT       = "#1d4ed8"
    SIDEBAR_TXT   = "#1e3a8a"
    ICON_COLOR    = "#2563eb"
    STAT_BG       = "#f8faff"
    DIVIDER       = "#e2e8f0"

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
    color: {STATUS_OK_TXT};
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}}
.status-warn {{
    background: {STATUS_WN_BG};
    color: {STATUS_WN_TXT};
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
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
#  SIDEBAR
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

    # Navigation
    st.markdown(f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:1px;color:{TEXT_MUTED};text-transform:uppercase;margin-bottom:8px;">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "nav",
        ["🏠  Home", "💬  Chatbot", "🧠  Trainer"],
        label_visibility="collapsed",
    )
    st.session_state.page = page

    st.markdown("---")

    # Status
    st.markdown(f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:1px;color:{TEXT_MUTED};text-transform:uppercase;margin-bottom:10px;">Status</div>', unsafe_allow_html=True)

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
    st.markdown(f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:1px;color:{TEXT_MUTED};text-transform:uppercase;margin-bottom:8px;">Appearance</div>', unsafe_allow_html=True)
    mode_label = "☀️ Switch to Light Mode" if dark else "🌙 Switch to Dark Mode"
    if st.button(mode_label, key="toggle_mode", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.72rem; color:{TEXT_MUTED}; text-align:center;">v1.0.0 · BankBot AI</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HOME PAGE
# ─────────────────────────────────────────────

if page == "🏠  Home":
    st.markdown(f"""
    <div class="page-header">
        <h1>Welcome to BankBot AI 🏦</h1>
        <p>Your intelligent 24×7 banking assistant — powered by natural language understanding.</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    total_examples = sum(len(i["examples"]) for i in st.session_state.intents)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(st.session_state.intents)}</div><div class="stat-label">Intents</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total_examples}</div><div class="stat-label">Training examples</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{"✓" if st.session_state.model_trained else "✗"}</div><div class="stat-label">Model trained</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(st.session_state.chat_history)}</div><div class="stat-label">Messages</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    st.markdown(f'<h2 style="color:{TEXT_PRIMARY}; margin-bottom:16px;">What can BankBot do?</h2>', unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns(4)
    features = [
        ("💰", "Balance Inquiry", "Check your account balance and get detailed breakdowns instantly."),
        ("💸", "Fund Transfers", "Transfer money to anyone via NEFT/IMPS with entity extraction."),
        ("🏠", "Loan Services", "Explore personal, home, car, and education loan options."),
        ("💳", "Credit Cards", "Apply, manage, block, or check credit card details."),
        ("📊", "Transactions", "View recent transactions and monthly spending summaries."),
        ("🏦", "Account Opening", "Open savings, current, or fixed deposit accounts digitally."),
        ("🏧", "ATM Services", "Find ATMs, change PIN, block debit cards."),
        ("🎧", "Support", "Connect to agents, raise complaints, track tickets."),
    ]
    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="feature-card">
                <span class="icon">{icon}</span>
                <div class="title">{title}</div>
                <div class="desc">{desc}</div>
            </div><br>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<h2 style="color:{TEXT_PRIMARY}; margin-bottom:12px;">Quick Start</h2>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px; padding:20px;">
        <p style="color:{TEXT_SECONDARY}; margin-bottom:12px; font-size:0.92rem;">
            <b>Step 1:</b> Go to <b>🧠 Trainer</b> and click <b>Train Model</b> (pre-loaded with 10 intents).<br>
            <b>Step 2:</b> Go to <b>💬 Chatbot</b> and start chatting!<br>
            <b>Step 3:</b> Add new intents in the Trainer anytime and retrain.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CHATBOT PAGE
# ─────────────────────────────────────────────

elif page == "💬  Chatbot":
    st.markdown(f"""
    <div class="page-header">
        <h1>💬 Chat with BankBot</h1>
        <p>Ask about your balance, transfers, loans, credit cards, or transactions.</p>
    </div>
    """, unsafe_allow_html=True)

    # Model status banner
    if not st.session_state.model_trained:
        st.warning("⚠️ Model not trained yet. Go to **🧠 Trainer** and click **Train Model** first.")
    else:
        st.markdown(f'<span class="status-ok">✅ Model ready — start chatting!</span><br><br>', unsafe_allow_html=True)

    # Quick action chips
    st.markdown(f'<div style="margin-bottom:12px; font-size:0.82rem; color:{TEXT_MUTED}; font-weight:600;">Quick actions:</div>', unsafe_allow_html=True)
    qa_cols = st.columns(6)
    quick_actions = [
        "Check my balance",
        "Show transactions",
        "Apply for a loan",
        "Transfer money",
        "Block my card",
        "Nearest ATM",
    ]
    for i, qa in enumerate(quick_actions):
        with qa_cols[i]:
            if st.button(qa, key=f"qa_{i}", use_container_width=True):
                if not st.session_state.model_trained:
                    reply = "⚠️ Please train the model first."
                    meta = {}
                else:
                    result   = predict_intent(qa)
                    entities = extract_entities(qa)
                    reply    = generate_response(result["intent"], entities)
                    meta     = result
                st.session_state.chat_history.append(("You",    qa,    {}))
                st.session_state.chat_history.append(("BankBot", reply, meta))
                st.rerun()

    st.markdown("---")

    # Input area
    st.markdown(f'<div class="chat-input-area">', unsafe_allow_html=True)
    inp_col, btn_col = st.columns([5, 1])
    with inp_col:
        user_input = st.text_input(
            "Message",
            placeholder="Type your banking query… e.g. 'What is my balance?'",
            key="chat_input",
            label_visibility="collapsed",
        )
    with btn_col:
        send = st.button("Send ➤", key="send_btn", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if send and user_input.strip():
        if not st.session_state.model_trained:
            reply = "⚠️ Model not trained. Please go to the **🧠 Trainer** page and train the model first."
            meta  = {}
        else:
            with st.spinner("Thinking…"):
                result   = predict_intent(user_input)
                entities = extract_entities(user_input)
                reply    = generate_response(result["intent"], entities)
                meta     = result
                time.sleep(0.3)  # slight pause for UX

        st.session_state.chat_history.append(("You",     user_input, {}))
        st.session_state.chat_history.append(("BankBot", reply,      meta))
        st.rerun()

    # Chat display
    if not st.session_state.chat_history:
        st.markdown(f"""
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

    # Debug panel (expandable)
    last_bot = [(m, meta) for s, m, meta in st.session_state.chat_history if s == "BankBot" and meta]
    if last_bot:
        with st.expander("🔍 Last prediction details", expanded=False):
            _, last_meta = last_bot[-1]
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Intent:** `{last_meta.get('intent','—')}`")
                st.markdown(f"**Confidence:** `{round(last_meta.get('confidence',0)*100, 1)}%`")
            with c2:
                if last_meta.get("all_scores"):
                    render_confidence_bars(last_meta["all_scores"])

    # Clear chat
    if st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear conversation", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ─────────────────────────────────────────────
#  TRAINER PAGE
# ─────────────────────────────────────────────

elif page == "🧠  Trainer":
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
