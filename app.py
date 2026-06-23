import streamlit as st
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from faq_data import FAQ_DATA
from faq_engine import FAQEngine


def send_verification_email(to_email: str, code: str) -> tuple:
    """Send a branded OTP email via Gmail SMTP.
    Returns (success: bool, error_key: str).
    """
    try:
        sender   = st.secrets["gmail"]["sender"]
        # Strip spaces — Google shows App Passwords with spaces but both forms work
        password = st.secrets["gmail"]["app_password"].replace(" ", "")
    except Exception:
        return False, "not_configured"

    html_body = f"""
    <html>
    <body style="margin:0;padding:0;background:#F5EDE6;font-family:Inter,sans-serif">
    <div style="max-width:480px;margin:40px auto;background:#FAF5F0;
                border-radius:16px;overflow:hidden;border:1px solid #E8C9B8">
        <div style="background:#3D2318;padding:24px;text-align:center">
            <div style="font-size:1.4rem;font-weight:700;color:#F2E8E0">🛍️ ShopAssist</div>
        </div>
        <div style="padding:28px 32px">
            <h2 style="color:#3D2318;font-size:1.1rem;margin:0 0 12px">
                Verify your new email address
            </h2>
            <p style="color:#5C3420;font-size:0.9rem;margin:0 0 20px">
                Use the code below to confirm your email change.
                It expires in <strong>10 minutes</strong>.
            </p>
            <div style="background:#3D2318;color:#F2E8E0;font-size:2.2rem;font-weight:700;
                        letter-spacing:0.35em;text-align:center;padding:22px;
                        border-radius:12px;margin:0 0 20px">{code}</div>
            <p style="color:#BFA89A;font-size:0.78rem;margin:0">
                If you did not request this change, you can safely ignore this email.
                Your current email will remain unchanged.
            </p>
        </div>
        <div style="background:#F5EDE6;padding:14px;text-align:center;
                    font-size:0.72rem;color:#BFA89A">
            © ShopAssist &nbsp;·&nbsp; Do not reply to this email
        </div>
    </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "ShopAssist — Your email verification code"
    msg["From"]    = f"ShopAssist <{sender}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))

    # Try SSL on port 465 first, fall back to STARTTLS on port 587
    for attempt in ("ssl", "tls"):
        try:
            if attempt == "ssl":
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender, password)
                    server.sendmail(sender, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(sender, password)
                    server.sendmail(sender, to_email, msg.as_string())
            return True, ""
        except smtplib.SMTPAuthenticationError:
            if attempt == "tls":
                return False, "auth_error"
            # try next method
        except Exception as e:
            if attempt == "tls":
                return False, str(e)
    return False, "auth_error"

st.set_page_config(
    page_title="ShopAssist — FAQ Chatbot",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #FAF5F0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #FAF5F0 0%, #F5EDE6 100%) !important;
}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    visibility: hidden !important; display: none !important;
}
header { visibility: hidden !important; }

/* Keep sidebar expand button visible when sidebar is collapsed */
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    display: flex !important;
    background: #3D2318 !important;
    border-radius: 0 10px 10px 0 !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] button svg { fill: #E8C9B8 !important; }
[data-testid="stSidebarCollapseButton"] button { color: #E8C9B8 !important; }

/* Fix chat message text colour (overrides Streamlit dark-mode injection) */
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong {
    color: #3D2318 !important;
}

/* Sidebar */
[data-testid="stSidebar"] { background: #3D2318 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: #F2E8E0 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F2E8E0 !important; }
[data-testid="stSelectbox"] > div > div {
    border: 1.5px solid #5C3420 !important;
    border-radius: 10px !important;
    background: #2E1A10 !important;
    color: #F2E8E0 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stTextInput"] input {
    background: #2E1A10 !important;
    border: 1.5px solid #5C3420 !important;
    border-radius: 10px !important;
    color: #F2E8E0 !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextInput"] label { color: #BFA89A !important; font-size: 0.72rem !important; }

/* Chat input */
[data-testid="stChatInput"] {
    border: 1.5px solid #E8C9B8 !important;
    border-radius: 14px !important;
    background: #FAF5F0 !important;
}
[data-testid="stChatInput"] textarea {
    background: #FAF5F0 !important;
    color: #3D2318 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #BFA89A !important; }
[data-testid="stChatInput"] button { background: #C9967A !important; border-radius: 10px !important; }

/* Buttons */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #C9967A 0%, #A8785C 100%) !important;
    color: #FAF5F0 !important; border: none !important; border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important; font-size: 0.84rem !important;
}
[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }

/* Sidebar components */
.sb-div  { height:1px; background:#5C3420; margin:12px 0; }
.sb-lbl  { font-size:0.58rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase;
           color:#BFA89A !important; display:block; margin-bottom:8px; }
.sb-brand{ font-family:'Cormorant Garamond',serif; font-size:1.15rem; font-weight:600;
           color:#F2E8E0 !important; margin-bottom:2px; }
.sb-tag  { font-size:0.7rem; color:#BFA89A !important; margin-bottom:14px; }

.sb-stat { background:#2E1A10; border-radius:10px; padding:10px 13px; margin-bottom:7px;
           display:flex; justify-content:space-between; align-items:center; }
.sb-stat-l { font-size:0.73rem; color:#BFA89A !important; }
.sb-stat-v { font-family:'Cormorant Garamond',serif; font-size:1.2rem;
             font-weight:600; color:#E8C9B8 !important; }

/* Category pills row */
.cat-pill-row { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px; }
.cat-pill {
    display:inline-block; padding:4px 12px; border-radius:20px;
    font-size:0.75rem; font-weight:500; cursor:pointer;
    border:1.5px solid #E8C9B8; background:#FAF5F0; color:#5C3420;
    transition:background 0.15s, border-color 0.15s;
    white-space:nowrap;
}
.cat-pill.active { background:#C9967A; border-color:#C9967A; color:#FAF5F0; }
.cat-pill:hover  { background:#E8C9B8; border-color:#C9967A; }

/* Account card */
.acct-card {
    background: #fff;
    border: 1.5px solid #E8C9B8;
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 14px;
}
.acct-avatar {
    width:42px; height:42px; border-radius:50%;
    background:#E8C9B8; color:#5C3420;
    display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; font-weight:600; flex-shrink:0;
}
.acct-name  { font-weight:600; font-size:0.95rem; color:#3D2318; }
.acct-email { font-size:0.75rem; color:#BFA89A; }

/* Dashboard quick-stats strip */
.dash-strip {
    display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:14px;
}
.dash-card {
    background:#fff; border:1.5px solid #E8C9B8; border-radius:12px;
    padding:12px 14px; text-align:center;
}
.dash-card-val { font-family:'Cormorant Garamond',serif; font-size:1.5rem;
                 font-weight:600; color:#3D2318; }
.dash-card-lbl { font-size:0.68rem; color:#BFA89A; margin-top:2px; }

/* History table */
.hist-row {
    display:flex; align-items:center; gap:10px;
    padding:9px 14px; border-radius:10px;
    background:#FAF5F0; border:1px solid #F0DDD0;
    margin-bottom:6px; font-size:0.82rem; color:#3D2318;
}
.hist-cat  { font-size:0.6rem; font-weight:600; letter-spacing:0.08em;
             text-transform:uppercase; padding:2px 8px; border-radius:20px;
             background:#3D2318; color:#E8C9B8; flex-shrink:0; }
.hist-conf { font-size:0.6rem; font-weight:600; padding:2px 8px; border-radius:20px; flex-shrink:0; }
.hist-conf.high   { background:#DFF0D8; color:#3D6B2E; }
.hist-conf.medium { background:#FEF3CD; color:#7A5B00; }
.hist-conf.low    { background:#F8D7DA; color:#6B2028; }
.hist-q    { flex:1; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.hist-time { font-size:0.68rem; color:#BFA89A; flex-shrink:0; }

/* Nav tabs */
.nav-tabs { display:flex; gap:0; margin-bottom:0; border-bottom:1.5px solid #E8C9B8; }
.nav-tab  {
    padding:10px 18px; font-size:0.85rem; font-weight:500; cursor:pointer;
    color:#BFA89A; border-bottom:2px solid transparent; margin-bottom:-1.5px;
    background:transparent; border-top:none; border-left:none; border-right:none;
    font-family:'Inter',sans-serif; transition:color 0.15s;
}
.nav-tab.active { color:#3D2318; border-bottom-color:#C9967A; }
.nav-tab:hover  { color:#5C3420; }
</style>
""", unsafe_allow_html=True)

# ── Engine ───────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_engine():
    return FAQEngine(FAQ_DATA)

engine = load_engine()

# ── Session state ────────────────────────────────────────────────────────────────
def is_clean(msgs):
    return all("<div" not in m.get("text","") and "<script" not in m.get("text","") for m in msgs)

defaults = {
    "messages": [], "answered": 0, "active_tab": "Chat",
    "user_name": "Guest User", "user_email": "guest@shopassist.com",
    "history": [],
    "pending_email": None, "verify_code": None,
    "verify_sent_at": 0, "email_send_error": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.messages and not is_clean(st.session_state.messages):
    st.session_state.messages = []
    st.session_state.answered = 0
    st.session_state.history  = []

# ── Sidebar ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown('<div class="sb-brand">🛍️ ShopAssist</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-tag">E-commerce FAQ Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # ── Account card ─────────────────────────────────────────────────────────────
    st.markdown('<span class="sb-lbl">Account</span>', unsafe_allow_html=True)

    initials = "".join(w[0].upper() for w in st.session_state.user_name.split()[:2])
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;
                background:#2E1A10;border-radius:12px;padding:11px 13px;margin-bottom:10px">
        <div style="width:38px;height:38px;border-radius:50%;background:#E8C9B8;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.95rem;font-weight:600;color:#5C3420;flex-shrink:0">{initials}</div>
        <div style="min-width:0">
            <div style="font-size:0.85rem;font-weight:600;color:#F2E8E0;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                {st.session_state.user_name}</div>
            <div style="font-size:0.68rem;color:#BFA89A;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis">
                {st.session_state.user_email}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Edit profile", expanded=False):
        new_name  = st.text_input("Name",  value=st.session_state.user_name,  key="inp_name")
        new_email = st.text_input("Email", value=st.session_state.user_email, key="inp_email")
        if st.button("Save", use_container_width=True, key="save_profile"):
            st.session_state.user_name = new_name.strip() or st.session_state.user_name
            if new_email.strip() != st.session_state.user_email:
                code = str(random.randint(100000, 999999))
                st.session_state.pending_email    = new_email.strip()
                st.session_state.verify_code      = code
                ok, err = send_verification_email(new_email.strip(), code)
                st.session_state.verify_sent_at   = time.time()
                st.session_state.email_send_error = None if ok else err
            st.rerun()

        if st.session_state.pending_email:
            elapsed   = time.time() - st.session_state.verify_sent_at
            expired   = elapsed > 600
            can_resend = elapsed > 60

            err = st.session_state.email_send_error
            if err == "not_configured":
                st.warning("Gmail not configured — fill in .streamlit/secrets.toml")
                st.markdown(f'<div style="font-size:0.7rem;color:#BFA89A;margin-bottom:4px">'
                            f'Demo code: <strong style="color:#E8C9B8">'
                            f'{st.session_state.verify_code}</strong></div>',
                            unsafe_allow_html=True)
            elif err == "auth_error":
                st.error("Gmail login failed. Demo code shown below while you fix it.")
                st.markdown(f'<div style="font-size:0.7rem;color:#BFA89A;margin-bottom:4px">'
                            f'Demo code: <strong style="color:#E8C9B8">'
                            f'{st.session_state.verify_code}</strong></div>',
                            unsafe_allow_html=True)
                st.markdown("""
                <div style="font-size:0.72rem;color:#BFA89A;margin-top:4px;line-height:1.7">
                <strong style="color:#E8C9B8">Fix checklist:</strong><br>
                1. <a href="https://myaccount.google.com/security" target="_blank"
                   style="color:#C9967A">Enable 2-Step Verification</a> on your Google account<br>
                2. Go to <a href="https://myaccount.google.com/apppasswords" target="_blank"
                   style="color:#C9967A">App Passwords</a> → create one → paste in secrets.toml<br>
                3. Use the <strong>App Password</strong>, NOT your regular Gmail password<br>
                4. Restart the app after saving secrets.toml
                </div>
                """, unsafe_allow_html=True)
            elif err:
                st.error(f"Failed to send email: {err}")
            else:
                st.markdown(f"""
                <div style="background:#FFF8E8;border:1.5px solid #D4B84A;border-radius:10px;
                            padding:10px 13px;margin-top:6px;font-size:0.78rem;color:#7A5B00">
                    📧 Code sent to <strong>{st.session_state.pending_email}</strong>.
                    Check your inbox{' — <strong>code expired, resend</strong>' if expired else ''}.
                </div>
                """, unsafe_allow_html=True)

            otp = st.text_input("Verification code", placeholder="6-digit code",
                                key="otp_input", label_visibility="collapsed")
            col_v, col_r, col_c = st.columns(3)
            with col_v:
                if st.button("Verify", use_container_width=True, key="btn_verify"):
                    if expired:
                        st.error("Code expired. Please resend.")
                    elif otp == st.session_state.verify_code:
                        st.session_state.user_email        = st.session_state.pending_email
                        st.session_state.inp_email         = st.session_state.pending_email
                        st.session_state.pending_email     = None
                        st.session_state.verify_code       = None
                        st.session_state.email_send_error  = None
                        st.toast("Email updated!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Incorrect code.")
            with col_r:
                if st.button("Resend", use_container_width=True, key="btn_resend",
                             disabled=not can_resend):
                    code = str(random.randint(100000, 999999))
                    st.session_state.verify_code      = code
                    ok, err = send_verification_email(st.session_state.pending_email, code)
                    st.session_state.verify_sent_at   = time.time()
                    st.session_state.email_send_error = None if ok else err
                    st.rerun()
            with col_c:
                if st.button("Cancel", use_container_width=True, key="btn_cancel"):
                    st.session_state.pending_email    = None
                    st.session_state.verify_code      = None
                    st.session_state.email_send_error = None
                    st.rerun()

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # ── Category filter ───────────────────────────────────────────────────────────
    st.markdown('<span class="sb-lbl">Filter by category</span>', unsafe_allow_html=True)
    categories = ["All Categories"] + engine.categories
    selected   = st.selectbox("cat", categories, label_visibility="collapsed", key="cat_select")

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    # ── Session stats ─────────────────────────────────────────────────────────────
    st.markdown('<span class="sb-lbl">Session overview</span>', unsafe_allow_html=True)
    total_q = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(f"""
    <div class="sb-stat"><span class="sb-stat-l">Questions asked</span>
        <span class="sb-stat-v">{total_q}</span></div>
    <div class="sb-stat"><span class="sb-stat-l">Answered</span>
        <span class="sb-stat-v">{st.session_state.answered}</span></div>
    <div class="sb-stat"><span class="sb-stat-l">FAQ database</span>
        <span class="sb-stat-v">{len(FAQ_DATA)}</span></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.answered = 0
        st.session_state.history  = []
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#3D2318;border-radius:16px 16px 0 0;padding:16px 24px;
            display:flex;align-items:center;gap:14px">
    <div style="width:42px;height:42px;border-radius:12px;background:#E8C9B8;
                display:flex;align-items:center;justify-content:center;
                font-size:20px;flex-shrink:0">🛍️</div>
    <div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;
                    font-weight:600;color:#F2E8E0;line-height:1.1">ShopAssist</div>
        <div style="font-size:0.72rem;color:#BFA89A;margin-top:2px">
            Your intelligent shopping support companion</div>
    </div>
    <div style="margin-left:auto;display:flex;align-items:center;gap:7px;
                background:rgba(255,255,255,0.07);border:1px solid rgba(232,201,184,0.2);
                border-radius:30px;padding:5px 14px;font-size:0.7rem;
                color:#E8C9B8;flex-shrink:0">
        <span style="width:7px;height:7px;background:#C9967A;
                     border-radius:50%;display:inline-block"></span>
        Online
    </div>
</div>
""", unsafe_allow_html=True)

# ── Nav tabs ──────────────────────────────────────────────────────────────────────
tab_col1, tab_col2, tab_col3, tab_col4 = st.columns([1, 1, 1, 1])
with tab_col1:
    if st.button("💬  Chat",      use_container_width=True, key="tab_chat"):
        st.session_state.active_tab = "Chat"
with tab_col2:
    if st.button("📊  Dashboard", use_container_width=True, key="tab_dash"):
        st.session_state.active_tab = "Dashboard"
with tab_col3:
    if st.button("🕑  History",   use_container_width=True, key="tab_hist"):
        st.session_state.active_tab = "History"
with tab_col4:
    if st.button("👤  Account",   use_container_width=True, key="tab_acct"):
        st.session_state.active_tab = "Account"

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

active = st.session_state.active_tab

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ════════════════════════════════════════════════════════════════════════════════
if active == "Chat":

    # Category pills row
    all_cats = ["All"] + engine.categories
    pills_html = '<div class="cat-pill-row">'
    for c in all_cats:
        is_active = (selected == c) or (c == "All" and selected == "All Categories")
        cls = "cat-pill active" if is_active else "cat-pill"
        pills_html += f'<span class="{cls}">{c}</span>'
    pills_html += '</div>'
    st.markdown(pills_html, unsafe_allow_html=True)

    # Welcome
    if not st.session_state.messages:
        samples = engine.sample_questions(selected, n=4)
        with st.chat_message("assistant", avatar="🛍️"):
            st.markdown("Welcome! I'm **ShopAssist** — your e-commerce support companion.")
            st.markdown("I can help with orders, payments, shipping, returns, accounts, and more.")
            st.markdown("**Try asking:**")
            for q in samples:
                st.markdown(f"› {q}")

    # Replay history
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🛍️"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["text"])
            if msg["role"] == "assistant" and msg.get("category"):
                conf   = msg.get("conf_label", "")
                cat    = msg.get("category", "")
                color  = {"high":"#DFF0D8","medium":"#FEF3CD","low":"#F8D7DA"}.get(conf,"#EEE")
                tcolor = {"high":"#3D6B2E","medium":"#7A5B00","low":"#6B2028"}.get(conf,"#555")
                st.markdown(
                    f'<span style="background:#3D2318;color:#E8C9B8;font-size:0.6rem;'
                    f'font-weight:600;letter-spacing:0.1em;text-transform:uppercase;'
                    f'padding:2px 9px;border-radius:20px;margin-right:6px">{cat}</span>'
                    f'<span style="background:{color};color:{tcolor};font-size:0.6rem;'
                    f'font-weight:600;padding:2px 8px;border-radius:20px">{conf}</span>',
                    unsafe_allow_html=True
                )

    # Input
    user_input = st.chat_input("Ask about orders, payments, delivery, returns…")

    if user_input and user_input.strip():
        text = user_input.strip()
        ts   = time.strftime("%H:%M")

        with st.chat_message("user", avatar="👤"):
            st.markdown(text)
        st.session_state.messages.append({"role":"user","text":text,"time":ts})

        result = engine.query(text, category=selected)

        with st.chat_message("assistant", avatar="🛍️"):
            if result["found"]:
                st.markdown(result["answer"])
                conf   = result["conf_label"]
                cat    = result["category"]
                color  = {"high":"#DFF0D8","medium":"#FEF3CD","low":"#F8D7DA"}.get(conf,"#EEE")
                tcolor = {"high":"#3D6B2E","medium":"#7A5B00","low":"#6B2028"}.get(conf,"#555")
                st.markdown(
                    f'<span style="background:#3D2318;color:#E8C9B8;font-size:0.6rem;'
                    f'font-weight:600;letter-spacing:0.1em;text-transform:uppercase;'
                    f'padding:2px 9px;border-radius:20px;margin-right:6px">{cat}</span>'
                    f'<span style="background:{color};color:{tcolor};font-size:0.6rem;'
                    f'font-weight:600;padding:2px 8px;border-radius:20px">{conf}</span>',
                    unsafe_allow_html=True
                )
                st.session_state.answered += 1
                st.session_state.history.append({
                    "q": text, "cat": cat, "conf": conf, "time": ts
                })
                st.session_state.messages.append({
                    "role":"assistant","text":result["answer"],"time":ts,
                    "conf_label":conf,"category":cat,"suggestions":[],
                })
            else:
                fallback = "I couldn't find an answer for that. Try rephrasing, or pick a category."
                st.markdown(fallback)
                sugg = result.get("suggestions",[])
                if sugg:
                    st.markdown("**You might mean:**")
                    for s in sugg[:3]:
                        st.markdown(f"› {s}")
                st.session_state.history.append({
                    "q": text, "cat": "—", "conf": "none", "time": ts
                })
                st.session_state.messages.append({
                    "role":"assistant","text":fallback,"time":ts,
                    "conf_label":"none","category":"","suggestions":sugg,
                })

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════
elif active == "Dashboard":
    hist = st.session_state.history
    total   = len(hist)
    ans     = sum(1 for h in hist if h["conf"] != "none")
    high_ct = sum(1 for h in hist if h["conf"] == "high")
    unans   = total - ans

    # Quick stats
    st.markdown(f"""
    <div class="dash-strip">
        <div class="dash-card">
            <div class="dash-card-val">{total}</div>
            <div class="dash-card-lbl">Total questions</div>
        </div>
        <div class="dash-card">
            <div class="dash-card-val">{ans}</div>
            <div class="dash-card-lbl">Answered</div>
        </div>
        <div class="dash-card">
            <div class="dash-card-val">{high_ct}</div>
            <div class="dash-card-lbl">High confidence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Category breakdown
    st.markdown('<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
                'text-transform:uppercase;color:#BFA89A;margin-bottom:10px">Questions by category</div>',
                unsafe_allow_html=True)

    cat_counts = {}
    for h in hist:
        c = h["cat"]
        cat_counts[c] = cat_counts.get(c, 0) + 1

    if cat_counts:
        max_count = max(cat_counts.values()) if cat_counts else 1
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            pct = int((count / max_count) * 100)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                <div style="font-size:0.82rem;color:#3D2318;min-width:160px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{cat}</div>
                <div style="flex:1;height:8px;background:#F0DDD0;border-radius:4px;overflow:hidden">
                    <div style="width:{pct}%;height:100%;background:#C9967A;border-radius:4px"></div>
                </div>
                <div style="font-size:0.82rem;font-weight:600;color:#5C3420;min-width:20px;text-align:right">{count}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#BFA89A;font-size:0.85rem;padding:20px 0;text-align:center">'
                    'No questions asked yet. Start chatting to see your breakdown.</div>',
                    unsafe_allow_html=True)

    # Unanswered
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
                'text-transform:uppercase;color:#BFA89A;margin-bottom:10px">Unanswered questions</div>',
                unsafe_allow_html=True)

    unans_items = [h for h in hist if h["conf"] == "none"]
    if unans_items:
        for h in unans_items[-5:]:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                        border-radius:9px;background:#FFF5F0;border:1px solid #F0C8B0;
                        margin-bottom:6px;font-size:0.82rem;color:#3D2318">
                <span style="font-size:0.65rem;font-weight:600;letter-spacing:0.08em;
                             text-transform:uppercase;padding:2px 8px;border-radius:20px;
                             background:#F8D7DA;color:#6B2028;flex-shrink:0">no match</span>
                <span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{h["q"]}</span>
                <span style="font-size:0.68rem;color:#BFA89A;flex-shrink:0">{h["time"]}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#BFA89A;font-size:0.85rem;padding:12px 0">All questions answered ✓</div>',
                    unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ════════════════════════════════════════════════════════════════════════════════
elif active == "History":
    hist = st.session_state.history

    if not hist:
        st.markdown('<div style="color:#BFA89A;font-size:0.88rem;padding:30px 0;text-align:center">'
                    'No conversation history yet.</div>', unsafe_allow_html=True)
    else:
        # Filter row
        filter_cats = ["All"] + sorted(set(h["cat"] for h in hist if h["cat"] != "—"))
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            filter_cat = st.selectbox("Filter", filter_cats,
                                       label_visibility="collapsed", key="hist_filter")
        with col_f2:
            if st.button("Clear history", use_container_width=True, key="clear_hist"):
                st.session_state.history  = []
                st.session_state.messages = []
                st.session_state.answered = 0
                st.rerun()

        filtered = hist if filter_cat == "All" else [h for h in hist if h["cat"] == filter_cat]

        st.markdown(f'<div style="font-size:0.75rem;color:#BFA89A;margin:8px 0 10px">'
                    f'{len(filtered)} question{"s" if len(filtered)!=1 else ""}</div>',
                    unsafe_allow_html=True)

        for h in reversed(filtered):
            conf   = h["conf"]
            color  = {"high":"#DFF0D8","medium":"#FEF3CD","low":"#F8D7DA","none":"#F0E0D8"}.get(conf,"#EEE")
            tcolor = {"high":"#3D6B2E","medium":"#7A5B00","low":"#6B2028","none":"#7A4030"}.get(conf,"#555")
            cat_bg = "#3D2318" if h["cat"] != "—" else "#BFA89A"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:9px 14px;
                        border-radius:10px;background:#FAF5F0;border:1px solid #F0DDD0;
                        margin-bottom:7px">
                <span style="font-size:0.6rem;font-weight:600;letter-spacing:0.08em;
                             text-transform:uppercase;padding:2px 8px;border-radius:20px;
                             background:{cat_bg};color:#E8C9B8;flex-shrink:0">{h["cat"]}</span>
                <span style="flex:1;min-width:0;font-size:0.83rem;color:#3D2318;
                             overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{h["q"]}</span>
                <span style="font-size:0.6rem;font-weight:600;padding:2px 8px;border-radius:20px;
                             background:{color};color:{tcolor};flex-shrink:0">{conf}</span>
                <span style="font-size:0.68rem;color:#BFA89A;flex-shrink:0">{h["time"]}</span>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — ACCOUNT
# ════════════════════════════════════════════════════════════════════════════════
elif active == "Account":

    initials_main = "".join(w[0].upper() for w in st.session_state.user_name.split()[:2])
    total_q_acct  = sum(1 for m in st.session_state.messages if m["role"] == "user")

    # ── Profile banner ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#3D2318;border-radius:16px;padding:22px 24px;
                display:flex;align-items:center;gap:18px;margin-bottom:18px">
        <div style="width:60px;height:60px;border-radius:50%;background:#E8C9B8;
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.4rem;font-weight:700;color:#5C3420;flex-shrink:0">
            {initials_main}
        </div>
        <div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:1.3rem;
                        font-weight:600;color:#F2E8E0;line-height:1.2">
                {st.session_state.user_name}
            </div>
            <div style="font-size:0.8rem;color:#BFA89A;margin-top:3px">
                {st.session_state.user_email}
            </div>
            <div style="margin-top:8px">
                <span style="background:#C9967A;color:#FAF5F0;font-size:0.65rem;font-weight:600;
                             letter-spacing:0.08em;text-transform:uppercase;
                             padding:3px 10px;border-radius:20px">Member</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats strip ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px">
        <div style="background:#fff;border:1.5px solid #E8C9B8;border-radius:12px;
                    padding:14px;text-align:center">
            <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;
                        font-weight:600;color:#3D2318">{total_q_acct}</div>
            <div style="font-size:0.68rem;color:#BFA89A;margin-top:2px">Questions asked</div>
        </div>
        <div style="background:#fff;border:1.5px solid #E8C9B8;border-radius:12px;
                    padding:14px;text-align:center">
            <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;
                        font-weight:600;color:#3D2318">{st.session_state.answered}</div>
            <div style="font-size:0.68rem;color:#BFA89A;margin-top:2px">Answered</div>
        </div>
        <div style="background:#fff;border:1.5px solid #E8C9B8;border-radius:12px;
                    padding:14px;text-align:center">
            <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;
                        font-weight:600;color:#3D2318">{len(FAQ_DATA)}</div>
            <div style="font-size:0.68rem;color:#BFA89A;margin-top:2px">FAQ entries</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Edit profile form ─────────────────────────────────────────────────────────
    st.markdown('<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
                'text-transform:uppercase;color:#BFA89A;margin-bottom:12px">Edit profile</div>',
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        acct_name  = st.text_input("Display name",  value=st.session_state.user_name,  key="acct_name")
    with col_b:
        acct_email = st.text_input("Email address", value=st.session_state.user_email, key="acct_email")

    if st.button("Save changes", use_container_width=True, key="acct_save"):
        st.session_state.user_name = acct_name.strip() or st.session_state.user_name
        if acct_email.strip() != st.session_state.user_email:
            code = str(random.randint(100000, 999999))
            st.session_state.pending_email    = acct_email.strip()
            st.session_state.verify_code      = code
            ok, err = send_verification_email(acct_email.strip(), code)
            st.session_state.verify_sent_at   = time.time()
            st.session_state.email_send_error = None if ok else err
        st.rerun()

    # ── Email verification notice ─────────────────────────────────────────────────
    if st.session_state.pending_email:
        elapsed    = time.time() - st.session_state.verify_sent_at
        expired    = elapsed > 600
        can_resend = elapsed > 60
        err = st.session_state.email_send_error

        if err == "not_configured":
            st.warning("Gmail not configured — fill in `.streamlit/secrets.toml` to send real emails.")
            st.markdown(f'<div style="font-size:0.78rem;color:#7A5B00;margin-bottom:6px">'
                        f'Demo code: <strong>{st.session_state.verify_code}</strong></div>',
                        unsafe_allow_html=True)
        elif err == "auth_error":
            st.error("Gmail login failed. Demo code shown below while you fix it.")
            st.markdown(f'<div style="font-size:0.82rem;color:#5C3420;margin:6px 0">'
                        f'Demo code: <strong>{st.session_state.verify_code}</strong></div>',
                        unsafe_allow_html=True)
            st.markdown("""
            <div style="background:#FFF3CD;border:1px solid #FFEAA0;border-radius:10px;
                        padding:12px 16px;font-size:0.8rem;color:#7A5B00;line-height:1.8">
                <strong>Fix checklist:</strong><br>
                1. <a href="https://myaccount.google.com/security" target="_blank"
                   style="color:#C9967A">Enable 2-Step Verification</a>
                   on your Google account<br>
                2. Open <a href="https://myaccount.google.com/apppasswords" target="_blank"
                   style="color:#C9967A">App Passwords</a>
                   → create a new one → copy the 16-character code<br>
                3. Paste it into <code>.streamlit/secrets.toml</code>
                   as <code>app_password</code>
                   (use your <strong>App Password</strong>, not your Gmail login password)<br>
                4. Restart the app — then try again
            </div>
            """, unsafe_allow_html=True)
        elif err:
            st.error(f"Could not send email: {err}")
        else:
            st.markdown(f"""
            <div style="background:#FFF8E8;border:1.5px solid #D4B84A;border-radius:12px;
                        padding:14px 18px;margin-top:14px">
                <div style="font-size:0.88rem;font-weight:600;color:#7A5B00;margin-bottom:6px">
                    📧 Verify your new email address
                </div>
                <div style="font-size:0.82rem;color:#7A5B00">
                    A 6-digit verification code has been sent to
                    <strong>{st.session_state.pending_email}</strong>.
                    Check your inbox and enter the code below.
                </div>
                <div style="font-size:0.72rem;color:#A89050;margin-top:8px">
                    {'⚠️ Code expired — click Resend to get a new one.' if expired
                     else f'Expires in {max(0, 10 - int(elapsed // 60))} min · Check spam if not received.'}
                </div>
            </div>
            """, unsafe_allow_html=True)

        otp_main = st.text_input("Enter verification code",
                                  placeholder="6-digit code", key="otp_main")
        col_m1, col_m2, col_m3 = st.columns([1, 1, 1])
        with col_m1:
            if st.button("Verify email", use_container_width=True, key="acct_verify"):
                if expired and err != "not_configured":
                    st.error("Code expired. Please resend.")
                elif otp_main == st.session_state.verify_code:
                    st.session_state.user_email        = st.session_state.pending_email
                    # Sync the text input widget so it shows the new email after rerun
                    st.session_state.acct_email        = st.session_state.pending_email
                    st.session_state.pending_email     = None
                    st.session_state.verify_code       = None
                    st.session_state.email_send_error  = None
                    st.toast("Email updated successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Incorrect code. Please try again.")
        with col_m2:
            if st.button("Resend code", use_container_width=True, key="acct_resend",
                         disabled=not can_resend):
                code = str(random.randint(100000, 999999))
                st.session_state.verify_code      = code
                ok, err2 = send_verification_email(st.session_state.pending_email, code)
                st.session_state.verify_sent_at   = time.time()
                st.session_state.email_send_error = None if ok else err2
                st.rerun()
        with col_m3:
            if st.button("Cancel", use_container_width=True, key="acct_cancel"):
                st.session_state.pending_email     = None
                st.session_state.verify_code       = None
                st.session_state.email_send_error  = None
                st.rerun()

    # ── Account details rows ──────────────────────────────────────────────────────
    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;font-weight:600;letter-spacing:0.1em;'
                'text-transform:uppercase;color:#BFA89A;margin-bottom:12px">Account details</div>',
                unsafe_allow_html=True)

    for label, value in [
        ("Account type",    "Standard member"),
        ("Preferred store", "ShopAssist Global"),
        ("Language",        "English"),
        ("Notifications",   "Email — enabled"),
    ]:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:11px 14px;background:#FAF5F0;border:1px solid #F0DDD0;
                    border-radius:10px;margin-bottom:7px">
            <span style="font-size:0.82rem;color:#BFA89A">{label}</span>
            <span style="font-size:0.82rem;font-weight:500;color:#3D2318">{value}</span>
        </div>
        """, unsafe_allow_html=True)
