import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import copy
import os
import traceback

# ==========================================
# 🔧 PAGE CONFIG — MUST BE ABSOLUTE FIRST
# ==========================================
st.set_page_config(
    page_title="Integrated DTI & LTV Analysis Engine",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🔐 AUTHENTICATION SYSTEM
# ==========================================
def _check_credentials(username: str, password: str) -> bool:
    try:
        return (username == st.secrets["auth"]["username"] and
                password == st.secrets["auth"]["password"])
    except Exception:
        return (username == "admin" and password == "admin")


def login_ui():
    """Render a centered login card using Streamlit columns + targeted CSS."""

    st.markdown("""
    <style>
    /* ── Hide chrome ─────────────────────────────────────────────── */
    [data-testid="stSidebar"]       { display: none !important; }
    #MainMenu, footer, header       { visibility: hidden !important; }

    /* ── Full-viewport gradient background ───────────────────────── */
    .stApp {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 40%, #312e81 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* ── Remove default padding so we control layout ─────────────── */
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* ── Vertically + horizontally centre the columns row ────────── */
    [data-testid="stAppViewContainer"] > section > div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        padding: 2rem 1rem !important;
    }

    /* ── The three-column wrapper: kill its own padding ──────────── */
    [data-testid="stHorizontalBlock"] {
        padding: 0 !important;
        gap: 0 !important;
    }

    /* ── Card styling applied to the CENTRE column ───────────────── */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
        background: #ffffff !important;
        border-radius: 20px !important;
        border: 1px solid rgba(99, 102, 241, 0.12) !important;
        box-shadow:
            0 4px 6px rgba(0, 0, 0, 0.03),
            0 20px 60px rgba(0, 0, 0, 0.25),
            0 0 0 1px rgba(255, 255, 255, 0.05) inset !important;
        padding: 0 !important;
        overflow: hidden !important;
        max-width: 460px !important;
        margin: 0 auto !important;
    }

    /* ── Header banner inside the card ───────────────────────────── */
    .login-header {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 55%, #7c3aed 100%);
        padding: 2.8rem 2rem 2.2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .login-header::before {
        content: '';
        position: absolute;
        top: -50%; left: -30%;
        width: 160%; height: 200%;
        background: radial-gradient(ellipse, rgba(255,255,255,0.10) 0%, transparent 60%);
        pointer-events: none;
    }
    .login-header .logo-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 0.8rem;
        position: relative;
        z-index: 1;
    }
    .login-header .app-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03em;
        margin-bottom: 0.35rem;
        position: relative;
        z-index: 1;
    }
    .login-header .app-sub {
        font-size: 0.78rem;
        color: rgba(255,255,255,0.72);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        position: relative;
        z-index: 1;
    }

    /* ── Body area ───────────────────────────────────────────────── */
    .login-body-area {
        padding: 2rem 2.2rem 2.4rem;
    }
    .login-body-area .welcome-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e1b4b;
        margin-bottom: 0.3rem;
    }
    .login-body-area .welcome-sub {
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.55;
        margin-bottom: 1.4rem;
    }
    .field-label {
        display: block;
        font-size: 0.8rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.35rem;
        margin-top: 1.1rem;
    }

    /* ── Input overrides (scoped to login) ───────────────────────── */
    div[data-testid="stTextInput"] > div > div {
        background: #f9fafb !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 10px !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stTextInput"] > div > div:focus-within {
        border-color: #7c3aed !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.10) !important;
    }
    div[data-testid="stTextInput"] > div > div > input {
        background: transparent !important;
        border: none !important;
        color: #111827 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 0.9rem !important;
    }
    div[data-testid="stTextInput"] > div > div > input::placeholder {
        color: #9ca3af !important;
    }
    div[data-testid="stTextInput"] label {
        display: none !important;
    }

    /* ── Sign-in button ──────────────────────────────────────────── */
    div.stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #4338ca 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.8rem 1.5rem !important;
        margin-top: 1.6rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.30) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.40) !important;
    }
    div.stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Error alert ─────────────────────────────────────────────── */
    .login-error-box {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 0.7rem 0.9rem;
        margin-top: 1rem;
        font-size: 0.82rem;
        color: #b91c1c;
        font-weight: 500;
        display: flex;
        gap: 0.5rem;
        align-items: flex-start;
    }

    /* ── Footer note ─────────────────────────────────────────────── */
    .login-footer {
        text-align: center;
        padding: 1rem 2rem 1.4rem;
        font-size: 0.72rem;
        color: #94a3b8;
        border-top: 1px solid #f1f5f9;
    }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    # ── Three-column layout: spacer | card | spacer ─────────────────
    _spacer_l, col_card, _spacer_r = st.columns([1, 2.2, 1])

    with col_card:
        # ── Header banner ───────────────────────────────────────────
        st.markdown("""
        <div class="login-header">
            <span class="logo-icon">🏦</span>
            <div class="app-title">Integrated Analysis Engine</div>
            <div class="app-sub">DTI &amp; LTV Credit Assessment Platform</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Body ────────────────────────────────────────────────────
        st.markdown("""
        <div class="login-body-area">
            <div class="welcome-title">Welcome Back</div>
            <div class="welcome-sub">
                Sign in with your institutional credentials to access
                the integrated credit analysis platform.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="field-label">Username</span>', unsafe_allow_html=True)
        username = st.text_input(
            label="username",
            placeholder="Enter your username",
            key="_login_u",
            label_visibility="collapsed",
            autocomplete="username"
        )

        st.markdown('<span class="field-label">Password</span>', unsafe_allow_html=True)
        password = st.text_input(
            label="password",
            placeholder="Enter your password",
            type="password",
            key="_login_p",
            label_visibility="collapsed",
            autocomplete="current-password"
        )

        clicked = st.button("Sign In →", key="_login_btn", use_container_width=True)

        err = st.session_state.get("_login_error", "")
        if err:
            st.markdown(
                f'<div class="login-error-box"><span>⚠️</span><span>{err}</span></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="login-footer">'
            'Secured connection · Institutional use only · v2.4.1'
            '</div>',
            unsafe_allow_html=True
        )

    # ── Credential validation (unchanged logic) ─────────────────────
    if clicked:
        u = str(username).strip()
        p = str(password).strip()
        if not u:
            st.session_state["_login_error"] = "Username is required to continue."
            st.rerun()
        elif not p:
            st.session_state["_login_error"] = "Password is required to continue."
            st.rerun()
        elif _check_credentials(u, p):
            st.session_state["authenticated"] = True
            st.session_state["auth_username"] = u
            st.session_state["_login_error"] = ""
            st.rerun()
        else:
            st.session_state["_login_error"] = (
                f'Invalid credentials for "{u}". '
                f'Please check your username and password and try again.'
            )
            st.rerun()


# ==========================================
# 🏠 AUTH GATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_username" not in st.session_state:
    st.session_state["auth_username"] = ""

if not st.session_state["authenticated"]:
    login_ui()
    st.stop()

# ==========================================
# 🎨 GLOBAL STYLES (post-login)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
* { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
.stApp {
    background: linear-gradient(145deg, #f0f4ff 0%, #faf5ff 50%, #ede9fe 100%) !important;
    font-family: 'Inter', sans-serif !important;
    color: #1a1f36;
}
.block-container { max-width: 96% !important; padding-top: 1.5rem !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    box-shadow: 4px 0 24px rgba(0,0,0,0.18);
}
[data-testid="stSidebar"] * { color: #e0e7ff; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.95) !important;
    color: #1e1b4b !important;
    font-weight: 600;
    border-radius: 8px;
}
[data-testid="stSidebar"] .stRadio > div {
    background: rgba(255,255,255,0.95) !important;
    border-radius: 8px;
    padding: 0.5rem !important;
    margin: 0.5rem 0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #1e1b4b !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
[data-testid="stSidebar"] .stRadio input[type="radio"] {
    accent-color: #7c3aed !important;
}
[data-testid="stSidebar"] .stExpander {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    margin-bottom: 1rem;
    overflow: hidden;
}
[data-testid="stSidebar"] .stExpander summary {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
    background: rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] .stExpander .streamlit-expanderContent {
    padding: 1rem !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 0.65rem 0.9rem !important;
    font-size: 0.95rem !important;
    background: #f8fafc !important;
    transition: all 0.2s;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
    background: white !important;
}

div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
    background-color: #7c3aed !important;
    border-color: #7c3aed !important;
    color: white !important;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #6d28d9 !important;
    border-color: #6d28d9 !important;
    transform: translateY(-1px);
}

.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);
    padding: 1.25rem 1.5rem;
    border-radius: 14px;
    border: 1px solid #ddd6fe;
    box-shadow: 0 4px 14px rgba(124,58,237,0.08);
}
.metric-label {
    font-size: 0.75rem; font-weight: 700; color: #7c3aed;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem;
}
.metric-value {
    font-size: 1.7rem; font-weight: 700; color: #1e1b4b;
    font-family: 'DM Mono', monospace; line-height: 1.1;
}

.status-banner {
    padding: 0.9rem 1.5rem; border-radius: 12px;
    font-weight: 700; font-size: 1rem;
    text-align: center; margin: 1.25rem 0;
}
.status-pass { background: #d1fae5; border: 2px solid #059669; color: #065f46; }
.status-fail { background: #fee2e2; border: 2px solid #dc2626; color: #991b1b; }

.input-section {
    background: white; padding: 2rem; border-radius: 16px;
    border-left: 4px solid #7c3aed;
    box-shadow: 0 8px 32px rgba(0,0,0,0.05); margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📋 POLICY DATA & CONFIGURATIONS  (UNCHANGED)
# ==========================================
LOAN_CONFIG = {
    "Personal Term Loan (PTL)": 2.0, "Personal OD": 2.0, "Share Loan": 2.0,
    "Mortgage Loan": 2.0, "Auto Loan": 2.0, "Home Loan": 1.428,
    "First Time Home Buyer": 1.25, "Education Loan": 2.0,
    "Professional OD": 2.0, "Professional T/L": 2.0,
    "HP Loan": 2.0, "HP Loan Commercial": 2.0, "HP Loan (Used)": 2.0,
    "HP Loan Commercial-EV": 2.0,
    "Cash Credit facility": 2.0, "Short Term Facility": 2.0,
    "Permanent WC Loan": 2.0, "Business Term Loan": 2.0
}
DEFAULT_TENURE = {
    "Personal OD": 1, "Home Loan": 15, "First Time Home Buyer": 20,
    "Share Loan": 1, "Professional OD": 1, "Professional T/L": 5
}
DEFAULT_LTV_POLICY = [
    {"Loan Type": "Home Loan",               "Max LTV%": 60.0,  "Unsecured": False},
    {"Loan Type": "Mortgage Loan",            "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "HP Loan",                  "Max LTV%": 60.0,  "Unsecured": False},
    {"Loan Type": "HP Loan Commercial",       "Max LTV%": 80.0,  "Unsecured": False},
    {"Loan Type": "HP Loan (Used)",           "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "HP Loan Commercial-EV",    "Max LTV%": 80.0,  "Unsecured": False},
    {"Loan Type": "First Time Home Buyer",    "Max LTV%": 80.0,  "Unsecured": False},
    {"Loan Type": "Personal Term Loan (PTL)", "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Education Loan",           "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Professional T/L",         "Max LTV%": None,  "Unsecured": False},
    {"Loan Type": "Professional OD",          "Max LTV%": None,  "Unsecured": False},
    {"Loan Type": "Cash Credit facility",     "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Short Term Facility",      "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Permanent WC Loan",        "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Business Term Loan",       "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Personal OD",              "Max LTV%": 50.0,  "Unsecured": False},
]
LOAN_TYPE_PREFIXES = {
    "Home Loan": "HL", "Mortgage Loan": "ML", "HP Loan": "HP",
    "HP Loan Commercial": "HPC", "HP Loan (Used)": "HPU",
    "HP Loan Commercial-EV": "HPEV", "First Time Home Buyer": "FTB",
    "Personal Term Loan (PTL)": "PTL", "Education Loan": "EDL",
    "Professional T/L": "PRTL", "Professional OD": "PROD",
    "Cash Credit facility": "CC", "Short Term Facility": "STF",
    "Permanent WC Loan": "PWC", "Business Term Loan": "BTL",
    "Personal OD": "POD", "Auto Loan": "AL", "Share Loan": "SL"
}
HP_FACILITY_TYPES = {"HP Loan", "HP Loan Commercial", "HP Loan (Used)", "HP Loan Commercial-EV"}
PROFESSIONAL_OD_CAP       = 500_000.0
PROFESSIONAL_TL_CAP       = 1_500_000.0
PROFESSIONAL_COMBINED_CAP = 1_500_000.0

# ==========================================
# 🏠 APP STATE INITIALIZATION  (UNCHANGED)
# ==========================================
def init_state():
    defaults = {
        'loans': [], 'income_sources': [], 'fmv_sources': [],
        'custom_scenarios': [], 'loan_id_counter': 0, 'fmv_id_counter': 0,
        'loan_type_counters': {}, 'ltv_policy': copy.deepcopy(DEFAULT_LTV_POLICY)
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ==========================================
# 🧮 HELPER & LTV ENGINE FUNCTIONS  (UNCHANGED)
# ==========================================
def get_policy_dict():
    return {
        p["Loan Type"]: (None if p["Unsecured"] else p["Max LTV%"])
        for p in st.session_state.ltv_policy
    }

def _is_hp_loan(loan_type: str) -> bool:
    return str(loan_type).strip() in HP_FACILITY_TYPES

def _next_fmv_id():
    fid = st.session_state.fmv_id_counter
    st.session_state.fmv_id_counter += 1
    return fid

def _generate_loan_account_id(loan_type: str) -> str:
    prefix = LOAN_TYPE_PREFIXES.get(loan_type, "LN")
    if prefix not in st.session_state.loan_type_counters:
        st.session_state.loan_type_counters[prefix] = 0
    st.session_state.loan_type_counters[prefix] += 1
    return f"{prefix}{st.session_state.loan_type_counters[prefix]:03d}"

def _check_professional_caps(l_type, l_amt, existing_loans):
    if l_type not in ("Professional OD", "Professional T/L"):
        return True, ""
    existing_od = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional OD")
    existing_tl = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional T/L")
    new_od = existing_od + (l_amt if l_type == "Professional OD" else 0.0)
    new_tl = existing_tl + (l_amt if l_type == "Professional T/L" else 0.0)
    if l_type == "Professional OD" and new_od > PROFESSIONAL_OD_CAP:
        return False, "Professional OD total exceeds cap."
    if l_type == "Professional T/L" and new_tl > PROFESSIONAL_TL_CAP:
        return False, "Professional T/L total exceeds cap."
    if (new_od + new_tl) > PROFESSIONAL_COMBINED_CAP:
        return False, "Combined Prof OD + T/L exceeds combined cap."
    return True, ""

def _loan_is_ltv_exempt(loan: dict) -> bool:
    policy = get_policy_dict()
    if policy.get(loan.get('Loan Type')) is None:
        return True
    if loan.get('override_ltv', False):
        return True
    has_assigned = (
        loan.get('collateral_mode') == 'assigned'
        and bool(loan.get('assigned_collateral_ids'))
    )
    if loan.get('tied_property_ids') and not has_assigned:
        return True
    return False

def run_portfolio_ltv(loans, fmv_sources):
    policy = get_policy_dict()
    fmv_sources = [s for s in fmv_sources if 'id' in s]
    fmv_id_set  = {s['id'] for s in fmv_sources}

    vehicle_ids  = {s['id'] for s in fmv_sources if s.get('IsVehicle')}
    property_ids = fmv_id_set - vehicle_ids
    collateral_fmv_map = {s['id']: s['Amount'] for s in fmv_sources}
    total_fmv_original = sum(s['Amount'] for s in fmv_sources)

    remaining_fmv     = {sid: collateral_fmv_map[sid] for sid in fmv_id_set}
    effective_fmv_denom = {}

    active_loans = [
        l for l in loans
        if not _loan_is_ltv_exempt(l)
        and policy.get(l['Loan Type']) is not None
        and (
            l.get('collateral_mode', 'pool') == 'pool'
            or (l.get('collateral_mode') == 'assigned' and bool(l.get('assigned_collateral_ids')))
        )
    ]

    for loan in active_loans:
        lid      = loan['_loan_id']
        mode     = loan.get('collateral_mode', 'pool')
        max_ltv  = policy.get(loan['Loan Type'])
        allowed_ids = vehicle_ids if _is_hp_loan(loan['Loan Type']) else property_ids

        if mode == 'pool':
            total_remaining = sum(remaining_fmv[cid] for cid in allowed_ids)
            effective_fmv_denom[lid] = total_remaining
            if total_remaining > 0 and max_ltv:
                req_fmv  = loan['Principal'] / (max_ltv / 100.0)
                consumed = min(req_fmv, total_remaining)
                for cid in allowed_ids:
                    proportion = remaining_fmv[cid] / total_remaining
                    remaining_fmv[cid] = max(0.0, remaining_fmv[cid] - consumed * proportion)
        else:
            cids      = [c for c in loan.get('assigned_collateral_ids', [])
                         if c in fmv_id_set and c in allowed_ids]
            available = sum(remaining_fmv.get(cid, 0.0) for cid in cids)
            effective_fmv_denom[lid] = available
            if available > 0 and max_ltv:
                req_fmv  = loan['Principal'] / (max_ltv / 100.0)
                consumed = min(req_fmv, available)
                for cid in cids:
                    proportion = remaining_fmv[cid] / available
                    remaining_fmv[cid] = max(0.0, remaining_fmv[cid] - consumed * proportion)

    results = []
    for loan in loans:
        lid       = loan['_loan_id']
        lt        = loan['Loan Type']
        principal = loan['Principal']
        mode      = loan.get('collateral_mode', 'pool')
        exempt    = _loan_is_ltv_exempt(loan)
        max_ltv   = policy.get(lt)

        exempt_reason = None
        if max_ltv is None:
            exempt_reason = "policy"
        elif loan.get('override_ltv', False):
            exempt_reason = "override"
        elif (loan.get('tied_property_ids')
              and not (mode == 'assigned' and bool(loan.get('assigned_collateral_ids')))):
            exempt_reason = "tieup"

        if exempt:
            results.append({
                **loan,
                'Max LTV%': None, 'Assigned FMV': 0.0, 'Pool FMV': 0.0,
                'Total FMV': 0.0, 'LTV%': None, 'Pass_Status': True,
                'Is_Unsecured': True, 'Collateral_Mode': mode,
                'No_FMV_Error': False, 'Exempt_Reason': exempt_reason
            })
            continue

        fmv_denom = effective_fmv_denom.get(lid, 0.0)
        if mode == 'pool':
            assigned_fmv_val = 0.0
            pool_fmv_val     = fmv_denom
            total_alloc      = fmv_denom
        else:
            assigned_fmv_val = fmv_denom
            pool_fmv_val     = 0.0
            total_alloc      = fmv_denom

        if total_alloc <= 0:
            ltv_pct = None; passes = False; no_fmv_error = True
        else:
            ltv_pct = principal / total_alloc * 100.0
            passes  = ltv_pct <= max_ltv
            no_fmv_error = False

        results.append({
            **loan,
            'Max LTV%': max_ltv, 'Assigned FMV': assigned_fmv_val,
            'Pool FMV': pool_fmv_val, 'Total FMV': total_alloc,
            'LTV%': ltv_pct, 'Pass_Status': passes,
            'Is_Unsecured': False, 'Collateral_Mode': mode,
            'No_FMV_Error': no_fmv_error, 'Exempt_Reason': None
        })

    secured_results          = [r for r in results if not r['Is_Unsecured']]
    total_secured_principal  = sum(r['Principal'] for r in secured_results)
    total_exposure           = sum(r['Principal'] for r in results)
    total_alloc_fmv_sum      = sum(r['Total FMV'] for r in secured_results)

    wtd_ltv      = (total_secured_principal / total_alloc_fmv_sum * 100.0
                    if total_alloc_fmv_sum > 0 else 0.0)
    aggregate_ltv = (total_secured_principal / total_fmv_original * 100.0
                     if total_fmv_original > 0 else 0.0)
    overall_pass  = all(r['Pass_Status'] for r in results)

    return results, {
        'total_fmv': total_fmv_original, 'total_exposure': total_exposure,
        'total_secured_principal': total_secured_principal,
        'total_alloc_fmv': total_alloc_fmv_sum,
        'wtd_ltv': wtd_ltv, 'aggregate_ltv': aggregate_ltv,
        'overall_pass': overall_pass
    }

# ==========================================
# 🧮 DTI ENGINE  (UNCHANGED)
# ==========================================
def calculate_obligation(loan_type, principal, rate, tenure):
    if principal <= 0 or rate <= 0:
        return 0.0
    r_monthly = (rate / 100) / 12
    if "OD" in loan_type or "Overdraft" in loan_type:
        return principal * r_monthly
    else:
        if tenure <= 0:
            return 0.0
        n_months = tenure * 12
        try:
            return (principal * r_monthly * ((1 + r_monthly) ** n_months)) / \
                   (((1 + r_monthly) ** n_months) - 1)
        except Exception:
            return 0.0

def run_waterfall_allocation(df, total_income):
    df_sorted = df.sort_values(by='Required Multiplier', ascending=False).reset_index(drop=True)
    run_inc   = total_income
    pass_flags, act_covs, snaps = [], [], []
    num_loans = len(df_sorted)

    for idx, row in df_sorted.iterrows():
        obl     = row['Obligation']
        req_mult= row['Required Multiplier']
        req_amt = obl * req_mult
        snaps.append(run_inc)
        is_last = (idx == num_loans - 1)

        if not is_last:
            if run_inc >= req_amt:
                act_covs.append(req_mult)
                pass_flags.append(True)
                run_inc -= req_amt
            else:
                actual = run_inc / obl if obl > 0 else 0
                act_covs.append(actual)
                pass_flags.append(False)
                run_inc = 0
        else:
            actual = run_inc / obl if obl > 0 else 0
            act_covs.append(actual)
            pass_flags.append(actual >= req_mult)

    df_sorted['Pass_Status']               = pass_flags
    df_sorted['Actual Coverage']           = act_covs
    df_sorted['Available_Income_Snapshot'] = snaps
    return df_sorted

# ==========================================
# 📄 PDF ENGINE  (CORRECTED — fpdf2-safe)
# ==========================================
class IntegratedPDFReport(FPDF):
    """Professional multi-section credit analysis report."""

    # Colours
    NAVY   = (0, 32, 96)
    GREEN  = (5, 150, 105)
    RED    = (220, 38, 38)
    GREY   = (100, 100, 100)
    BLACK  = (0, 0, 0)
    WHITE  = (255, 255, 255)

    def __init__(self, client_name="", date_str="", **kwargs):
        super().__init__(**kwargs)
        self.client_name = client_name
        self.date_str    = date_str

    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(*self.NAVY)
        self.cell(0, 10, 'Integrated Credit Analysis Report', 0, 1, 'C')
        self.ln(2)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.GREY)
        self.cell(95, 5, f"Client: {self.client_name}", 0, 0, 'L')
        self.cell(0,  5, f"Date: {self.date_str}",      0, 1, 'R')
        self.ln(4)
        self.set_draw_color(*self.NAVY)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*self.GREY)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

    # ── Convenience helpers ─────────────────────────────────────────
    def section_title(self, title: str):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*self.NAVY)
        self.cell(0, 8, title, 0, 1)
        self.ln(2)

    def sub_title(self, title: str):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.NAVY)
        self.cell(0, 6, title, 0, 1)
        self.ln(1)

    def kv_row(self, left_label, left_val, right_label, right_val):
        self.set_font('Helvetica', '', 9)
        self.set_text_color(*self.BLACK)
        self.cell(95, 5, f"{left_label}: {left_val}", 0, 0)
        self.cell(0,  5, f"{right_label}: {right_val}", 0, 1)

    def table_header(self, widths, headers):
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(*self.BLACK)
        self.set_fill_color(235, 238, 245)
        for i, h in enumerate(headers):
            self.cell(widths[i], 6, h, 1, 0,
                      'C' if i > 0 else 'L', fill=True)
        self.ln()

    def table_row(self, widths, values, aligns=None, bold=False,
                  color=None, fill=False):
        if aligns is None:
            aligns = ['L'] + ['R'] * (len(values) - 1)
        self.set_font('Helvetica', 'B' if bold else '', 7)
        if color:
            self.set_text_color(*color)
        else:
            self.set_text_color(*self.BLACK)
        if fill:
            self.set_fill_color(248, 249, 252)
        for i, v in enumerate(values):
            self.cell(widths[i], 5, str(v), 1, 0, aligns[i], fill=fill)
        self.ln()


def _safe_pdf_bytes(pdf: FPDF) -> bytes:
    """
    Return PDF content as bytes regardless of fpdf / fpdf2 version.

    fpdf2  (>= 2.x) : pdf.output() returns bytes directly.
    fpdf   (1.x)    : pdf.output(dest='S') returns a Latin-1 str.
    """
    try:
        # fpdf2 ≥ 2.7 prefers no-arg; older fpdf2 accepts dest='S'
        result = pdf.output()
    except TypeError:
        result = pdf.output(dest='S')

    if isinstance(result, (bytes, bytearray)):
        return bytes(result)
    # Legacy fpdf 1.x returns a Latin-1 string
    if isinstance(result, str):
        return result.encode('latin-1')
    # Last resort
    return bytes(result)


def generate_integrated_pdf(client_name: str, report_data: dict) -> bytes:
    """Build the full PDF report and return raw bytes."""

    date_str = datetime.now().strftime("%B %d, %Y")
    pdf = IntegratedPDFReport(
        client_name=client_name,
        date_str=date_str,
        orientation='P',
        unit='mm',
        format='A4'
    )
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Unpack payload ──────────────────────────────────────────────
    gross_income     = report_data.get('gross_income', 0)
    eff_income       = report_data.get('eff_income', 0)
    scenario_name    = report_data.get('scenario_name', 'Baseline')
    stress_rate      = report_data.get('stress_rate', 0)
    stress_inc       = report_data.get('stress_inc', 0)
    enable_stress    = report_data.get('enable_stress', False)
    dti_overall_pass = report_data.get('dti_overall_pass', True)
    dti_agg_dti      = report_data.get('dti_agg_dti', 0)
    dti_shortfall    = report_data.get('dti_shortfall', 0)
    df_dti_res       = report_data.get('df_dti_res')
    ltv_results      = report_data.get('ltv_results', [])
    ltv_summary      = report_data.get('ltv_summary', {})
    total_fmv        = ltv_summary.get('total_fmv', 0)
    total_exposure   = ltv_summary.get('total_exposure', 0)
    aggregate_ltv    = ltv_summary.get('aggregate_ltv', 0)
    ltv_overall_pass = ltv_summary.get('overall_pass', True)
    income_sources   = report_data.get('income_sources', [])
    fmv_sources      = report_data.get('fmv_sources', [])

    overall_pass = dti_overall_pass and ltv_overall_pass

    # ═══════════════════════════════════════════════════════════════
    # PAGE 1 — Executive Summary
    # ═══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title('Executive Summary')

    # Assessment banner
    pdf.set_font('Helvetica', 'B', 11)
    if overall_pass:
        pdf.set_text_color(*pdf.GREEN)
        pdf.cell(0, 7, 'OVERALL ASSESSMENT:  APPROVED', 0, 1)
    else:
        pdf.set_text_color(*pdf.RED)
        pdf.cell(0, 7, 'OVERALL ASSESSMENT:  DECLINED', 0, 1)
    pdf.ln(3)

    pdf.kv_row("Monthly Gross Income", f"Rs. {gross_income:,.2f}",
               "Total Loan Exposure",  f"Rs. {total_exposure:,.2f}")

    inc_label = ("Effective Income (Post-Stress)" if enable_stress
                 else "Effective Income (Baseline)")
    pdf.kv_row(inc_label, f"Rs. {eff_income:,.2f}",
               "Total Collateral FMV", f"Rs. {total_fmv:,.2f}")

    pdf.kv_row("Aggregate DTI Coverage", f"{dti_agg_dti:.2f}x",
               "Aggregate LTV%",         f"{aggregate_ltv:.2f}%")

    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 9)
    dti_status = 'PASS' if dti_overall_pass else 'FAIL'
    ltv_status = 'PASS' if ltv_overall_pass else 'FAIL'
    dti_col = pdf.GREEN if dti_overall_pass else pdf.RED
    ltv_col = pdf.GREEN if ltv_overall_pass else pdf.RED

    pdf.set_text_color(*dti_col)
    pdf.cell(95, 5, f"DTI Status: {dti_status}  |  Shortfall: Rs. {dti_shortfall:,.2f}", 0, 0)
    pdf.set_text_color(*ltv_col)
    pdf.cell(0, 5, f"LTV Status: {ltv_status}", 0, 1)
    pdf.ln(4)

    # ═══════════════════════════════════════════════════════════════
    # PAGE 2 — DTI Analysis
    # ═══════════════════════════════════════════════════════════════
    if df_dti_res is not None and not df_dti_res.empty:
        pdf.add_page()
        pdf.section_title('Debt-to-Income (DTI) Analysis')

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(*pdf.BLACK)
        pdf.cell(0, 5, f"Active Scenario: {scenario_name}", 0, 1)
        if enable_stress:
            pdf.cell(0, 5,
                     f"Interest Rate Shock: +{stress_rate:.2f}%  |  "
                     f"Income Reduction: -{stress_inc:.2f}%", 0, 1)
        pdf.ln(2)

        # Income sources
        if income_sources:
            pdf.sub_title('Income Sources')
            w = [120, 70]
            pdf.table_header(w, ['Source', 'Amount (Rs.)'])
            for src in income_sources:
                pdf.table_row(w, [src['Source'], f"{src['Amount']:,.2f}"])
            pdf.table_row(w, ['Total', f"{gross_income:,.2f}"], bold=True)
            pdf.ln(4)

        # Waterfall table
        pdf.sub_title('Priority Allocation Breakdown')
        col_w   = [45, 25, 25, 25, 25, 25, 20]
        headers = ["Facility Type", "Principal", "Payment",
                   "Rem. Income", "Act. Cov.", "Req. Cov.", "Status"]
        pdf.table_header(col_w, headers)

        for row_idx, (_, row) in enumerate(df_dti_res.iterrows()):
            status = "PASS" if row['Pass_Status'] else "FAIL"
            row_color = pdf.GREEN if row['Pass_Status'] else pdf.RED
            fill = (row_idx % 2 == 1)
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(*pdf.BLACK)
            pdf.set_fill_color(248, 249, 252) if fill else None
            pdf.cell(col_w[0], 5, str(row['Loan Type'])[:22], 1, 0, 'L', fill=fill)
            pdf.cell(col_w[1], 5, f"{row['Amount']:,.0f}", 1, 0, 'R', fill=fill)
            pdf.cell(col_w[2], 5, f"{row['Obligation']:,.0f}", 1, 0, 'R', fill=fill)
            pdf.cell(col_w[3], 5, f"{row['Available_Income_Snapshot']:,.0f}", 1, 0, 'R', fill=fill)
            pdf.cell(col_w[4], 5, f"{row['Actual Coverage']:.2f}x", 1, 0, 'R', fill=fill)
            pdf.cell(col_w[5], 5, f"{row['Required Multiplier']:.2f}x", 1, 0, 'R', fill=fill)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.set_text_color(*row_color)
            pdf.cell(col_w[6], 5, status, 1, 1, 'C', fill=fill)

    # ═══════════════════════════════════════════════════════════════
    # PAGE 3 — LTV Analysis
    # ═══════════════════════════════════════════════════════════════
    if ltv_results:
        pdf.add_page()
        pdf.section_title('Loan-to-Value (LTV) Analysis')

        # Collateral table
        if fmv_sources:
            pdf.sub_title('Collateral & Fair Market Value Sources')
            cw = [60, 40, 40, 50]
            pdf.table_header(cw, ['Property Ref.', 'Owner', 'Type', 'FMV (Rs.)'])
            for src in fmv_sources:
                ctype = "Vehicle" if src.get('IsVehicle') else "Property"
                pdf.table_row(cw, [
                    src.get('Plot', 'N/A'),
                    src.get('Owner', 'N/A'),
                    ctype,
                    f"{src.get('Amount', 0):,.0f}"
                ])
            pdf.table_row(cw, ['', '', 'Total FMV', f"{total_fmv:,.0f}"], bold=True)
            pdf.ln(4)

        # Facility LTV table
        pdf.sub_title('Facility LTV Breakdown')
        col_w   = [20, 40, 30, 30, 20, 20, 30]
        headers = ["A/C No.", "Facility Type", "Principal",
                   "Total FMV", "LTV%", "Max LTV%", "Status"]
        pdf.table_header(col_w, headers)

        for row_idx, row in enumerate(ltv_results):
            is_unsec = row.get('Is_Unsecured', False)
            ltv_val  = row.get('LTV%')
            max_ltv  = row.get('Max LTV%')

            if is_unsec:
                ltv_text = "EXEMPT"
                max_disp = "N/A"
            elif row.get('No_FMV_Error'):
                ltv_text = "NO FMV"
                max_disp = f"{max_ltv:.0f}%" if max_ltv else "N/A"
            else:
                ltv_text = f"{ltv_val:.2f}%" if ltv_val is not None else "N/A"
                max_disp = f"{max_ltv:.0f}%" if max_ltv else "N/A"

            status   = "PASS" if row['Pass_Status'] else "FAIL"
            fmv_disp = 'N/A' if is_unsec else f"{row['Total FMV']:,.0f}"
            row_color = pdf.GREEN if row['Pass_Status'] else pdf.RED
            fill = (row_idx % 2 == 1)

            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(*pdf.BLACK)
            if fill:
                pdf.set_fill_color(248, 249, 252)
            pdf.cell(col_w[0], 5, row.get('loan_account_id', 'N/A'), 1, 0, 'L', fill=fill)
            pdf.cell(col_w[1], 5, str(row['Loan Type'])[:22], 1, 0, 'L', fill=fill)
            pdf.cell(col_w[2], 5, f"{row['Principal']:,.0f}", 1, 0, 'R', fill=fill)
            pdf.cell(col_w[3], 5, fmv_disp, 1, 0, 'R', fill=fill)
            pdf.cell(col_w[4], 5, ltv_text, 1, 0, 'R', fill=fill)
            pdf.cell(col_w[5], 5, max_disp, 1, 0, 'R', fill=fill)
            pdf.set_font('Helvetica', 'B', 7)
            pdf.set_text_color(*row_color)
            pdf.cell(col_w[6], 5, status, 1, 1, 'C', fill=fill)

        # Aggregate row
        agg_status = 'PASS' if ltv_overall_pass else 'FAIL'
        agg_color  = pdf.GREEN if ltv_overall_pass else pdf.RED
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_text_color(*pdf.BLACK)
        pdf.set_fill_color(235, 238, 245)
        pdf.cell(col_w[0] + col_w[1], 6, 'AGGREGATE', 1, 0, 'L', fill=True)
        pdf.cell(col_w[2], 6, f"{total_exposure:,.0f}", 1, 0, 'R', fill=True)
        pdf.cell(col_w[3], 6, f"{total_fmv:,.0f}", 1, 0, 'R', fill=True)
        pdf.cell(col_w[4], 6, f"{aggregate_ltv:.2f}%", 1, 0, 'R', fill=True)
        pdf.cell(col_w[5], 6, 'N/A', 1, 0, 'R', fill=True)
        pdf.set_text_color(*agg_color)
        pdf.cell(col_w[6], 6, agg_status, 1, 1, 'C', fill=True)

    # ── Return bytes ────────────────────────────────────────────────
    return _safe_pdf_bytes(pdf)


# ==========================================
# 📐 SIDEBAR CONFIGURATION  (UNCHANGED LOGIC)
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Configuration Panel")

    with st.expander("💰 Income & Stress Configuration (DTI)", expanded=True):
        inc_mode    = st.radio("Income Entry Method", ["Single Total", "Multiple Sources"])
        gross_income = 0.0

        if inc_mode == "Single Total":
            gross_income = st.number_input("Monthly Gross Income (Rs.)",
                                           value=150000.0, step=5000.0)
        else:
            c1, c2 = st.columns([1.5, 1])
            src = c1.text_input("Income Source")
            amt = c2.number_input("Amount (Rs.)", min_value=0.0)
            if st.button("➕ Add Source", type="primary"):
                if src.strip() and amt > 0:
                    st.session_state.income_sources.append(
                        {"Source": src.strip(), "Amount": amt}
                    )
                    st.rerun()
            if st.session_state.income_sources:
                st.dataframe(pd.DataFrame(st.session_state.income_sources), hide_index=True)
                if st.button("Clear All Sources"):
                    st.session_state.income_sources = []
                    st.rerun()
                gross_income = sum(x['Amount'] for x in st.session_state.income_sources)

        st.markdown("---")
        enable_stress  = st.toggle("Enable Stress Testing", value=False)
        stress_rate_val, stress_inc_val = 0.0, 0.0
        scenario_name  = "Baseline (No Stress)"
        stressed_sources_selection = []

        if enable_stress:
            if inc_mode == "Multiple Sources" and st.session_state.income_sources:
                all_src = [x['Source'] for x in st.session_state.income_sources]
                stressed_sources_selection = st.multiselect(
                    "Select Sources to Stress", all_src, default=all_src
                )

            with st.form("create_scenario_form"):
                fc1, fc2 = st.columns(2)
                c_name = fc1.text_input("Scenario Name")
                c_rate = fc2.number_input("Rate Shock (+%)", 0.0, 50.0, 2.0, step=0.5)
                c_inc  = st.number_input("Income Reduction (-%)", 0.0, 100.0, 10.0, step=5.0)
                if st.form_submit_button("Save Scenario", type="primary"):
                    if c_name:
                        st.session_state.custom_scenarios.append(
                            {"Name": c_name, "Rate": c_rate, "Income": c_inc}
                        )
                        st.rerun()

            if st.session_state.custom_scenarios:
                c_names      = [s['Name'] for s in st.session_state.custom_scenarios]
                active_c_name= st.selectbox("Active Scenario", c_names)
                active_s     = next(
                    (s for s in st.session_state.custom_scenarios if s['Name'] == active_c_name),
                    None
                )
                if active_s:
                    stress_rate_val = active_s['Rate']
                    stress_inc_val  = active_s['Income']
                    scenario_name   = active_c_name

    with st.expander("🏠 Collateral Configuration (LTV)", expanded=True):
        sb_plot      = st.text_input("Property Reference", placeholder="e.g. Plot 42-B")
        sb_owner     = st.text_input("Owner Name",         placeholder="e.g. John Doe")
        sb_fmv       = st.number_input("Fair Market Value (Rs.)", min_value=0.0, step=50000.0)
        sb_coll_type = st.radio("Collateral Type", ["Property", "Vehicle"])

        if st.button("Add Property", type="primary"):
            if sb_fmv > 0 and sb_plot.strip():
                st.session_state.fmv_sources.append({
                    "id": _next_fmv_id(),
                    "Plot": sb_plot.strip(), "Owner": sb_owner.strip(),
                    "Amount": sb_fmv, "IsVehicle": (sb_coll_type == "Vehicle")
                })
                st.rerun()

        if st.session_state.fmv_sources:
            st.markdown(
                f"**Total FMV:** Rs. "
                f"{sum(s['Amount'] for s in st.session_state.fmv_sources):,.0f}"
            )
            for src in st.session_state.fmv_sources:
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    tag = "🚗 " if src.get('IsVehicle') else "🏠 "
                    st.markdown(f"{tag} **{src['Plot']}** — Rs. {src['Amount']:,.0f}")
                with col_b:
                    if st.button("X", key=f"del_fmv_{src['id']}"):
                        st.session_state.fmv_sources = [
                            s for s in st.session_state.fmv_sources if s['id'] != src['id']
                        ]
                        for loan in st.session_state.loans:
                            if src['id'] in loan.get('assigned_collateral_ids', []):
                                loan['assigned_collateral_ids'].remove(src['id'])
                            if src['id'] in loan.get('tied_property_ids', []):
                                loan['tied_property_ids'].remove(src['id'])
                        st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset All Data", type="primary", use_container_width=True):
        for k in ['loans', 'income_sources', 'fmv_sources', 'custom_scenarios']:
            st.session_state[k] = []
        for k in ['loan_id_counter', 'fmv_id_counter']:
            st.session_state[k] = 0
        st.session_state['loan_type_counters'] = {}
        st.rerun()

# ==========================================
# 🖥️ MAIN DASHBOARD  (UNCHANGED LOGIC)
# ==========================================
st.title("🏦 Integrated DTI & LTV Analysis Engine")
st.markdown("Unified credit assessment for Debt-to-Income and Loan-to-Value metrics.")

with st.container():
    st.markdown("<div class='input-section'><h5>➕ Add New Facility</h5>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
    with c1: l_type = st.selectbox("Facility Type", list(LOAN_CONFIG.keys()))
    with c2: l_amt  = st.number_input("Principal Amount (Rs.)", step=10000.0, min_value=0.0)
    with c3: l_rate = st.number_input("Interest Rate (%)", value=12.0, step=0.25)
    with c4: l_ten  = st.number_input("Tenure (Years)", value=DEFAULT_TENURE.get(l_type, 5), min_value=1)

    st.markdown("#### DTI Parameters")
    c_opt, c_btn = st.columns([3, 1])
    with c_opt:
        use_man = st.checkbox("Use Fixed Monthly Payment (Override EMI)")
    man_emi = st.number_input("Fixed Monthly Payment (Rs.)", 0.0, step=1000.0) if use_man else 0.0

    st.markdown("#### LTV Parameters")
    policy_dict = get_policy_dict()
    max_ltv_sel = policy_dict.get(l_type)
    is_hp       = _is_hp_loan(l_type)

    override_ltv   = False
    coll_mode      = "pool"
    selected_colls = []
    tie_up_colls   = []

    if max_ltv_sel is not None:
        override_ltv = st.checkbox("Override collateral requirement (LTV Exempt)")
        if not override_ltv:
            use_dedicated = st.checkbox("Assign dedicated collateral?")
            coll_mode = "assigned" if use_dedicated else "pool"
            if use_dedicated:
                eligible = [s for s in st.session_state.fmv_sources
                            if bool(s.get('IsVehicle')) == is_hp]
                if eligible:
                    opts      = {f"{s['Plot']} - Rs.{s['Amount']:,.0f}": s['id'] for s in eligible}
                    sel_labels= st.multiselect("Select Collateral(s)", list(opts.keys()))
                    selected_colls = [opts[lbl] for lbl in sel_labels]
                else:
                    st.warning(f"No {'Vehicle' if is_hp else 'Property'} collateral available.")

        use_tie_up = st.checkbox("Tie up Property (additional security)?")
        if use_tie_up and st.session_state.fmv_sources:
            opts    = {f"{s['Plot']} - Rs.{s['Amount']:,.0f}": s['id']
                       for s in st.session_state.fmv_sources}
            tie_sel = st.multiselect("Select properties to tie up", list(opts.keys()))
            tie_up_colls = [opts[lbl] for lbl in tie_sel]
    else:
        st.info("Unsecured facility — no collateral required for LTV.")

    if c_btn.button("Add to Portfolio", type="primary", use_container_width=True):
        errors = []
        if l_amt  <= 0: errors.append("Principal must be > 0")
        if l_rate <= 0: errors.append("Rate must be > 0")
        if l_ten  <= 0: errors.append("Tenure must be >= 1")
        if use_man and man_emi <= 0: errors.append("Fixed EMI must be > 0")

        cap_ok, cap_msg = _check_professional_caps(l_type, l_amt, st.session_state.loans)
        if not cap_ok: errors.append(cap_msg)

        if errors:
            for e in errors: st.error(e)
        else:
            std_emi = calculate_obligation(l_type, l_amt, l_rate, l_ten)
            lid     = st.session_state.loan_id_counter
            st.session_state.loan_id_counter += 1
            ac_id   = _generate_loan_account_id(l_type)

            st.session_state.loans.append({
                "Loan Type": l_type, "Principal": l_amt,
                "Base Rate": l_rate, "Tenure": l_ten,
                "Base_Obligation": man_emi if use_man else std_emi,
                "Required Multiplier": LOAN_CONFIG[l_type],
                "Is_Manual": use_man, "_loan_id": lid, "loan_account_id": ac_id,
                "collateral_mode": coll_mode,
                "assigned_collateral_ids": selected_colls,
                "tied_property_ids": tie_up_colls,
                "override_ltv": override_ltv
            })
            st.success(f"✅ Added [{ac_id}] {l_type}")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 📊 ANALYSIS & RESULTS  (UNCHANGED LOGIC)
# ==========================================
if st.session_state.loans:
    # Effective income after stress
    eff_income = gross_income
    if enable_stress:
        if inc_mode == "Multiple Sources" and stressed_sources_selection:
            var_inc    = sum(x['Amount'] for x in st.session_state.income_sources
                            if x['Source'] in stressed_sources_selection)
            fix_inc    = gross_income - var_inc
            eff_income = fix_inc + var_inc * (1.0 - stress_inc_val / 100.0)
        else:
            eff_income = gross_income * (1.0 - stress_inc_val / 100.0)

    df_dti = pd.DataFrame(st.session_state.loans)
    df_dti['Amount'] = df_dti['Principal']

    def get_stress_row(row, s_rate):
        if row['Is_Manual']:
            return row['Base_Obligation'], row['Base Rate']
        new_r = row['Base Rate'] + s_rate
        return calculate_obligation(row['Loan Type'], row['Amount'], new_r, row['Tenure']), new_r

    df_dti[['Obligation', 'Effective_Rate']] = df_dti.apply(
        lambda x: pd.Series(get_stress_row(x, stress_rate_val)), axis=1
    )
    df_dti_res = run_waterfall_allocation(df_dti, eff_income)

    dti_overall_pass = all(df_dti_res['Pass_Status'])
    total_obl        = df_dti_res['Obligation'].sum()
    dti_agg_dti      = eff_income / total_obl if total_obl > 0 else 0

    dti_shortfall = 0.0
    if not dti_overall_pass:
        req_ideal     = sum(r['Obligation'] * r['Required Multiplier']
                            for _, r in df_dti_res.iterrows())
        dti_shortfall = max(0, req_ideal - eff_income)

    ltv_results, ltv_summary = run_portfolio_ltv(
        st.session_state.loans, st.session_state.fmv_sources
    )
    ltv_overall_pass = ltv_summary['overall_pass']

    # ── DTI Display ──────────────────────────────────────────────────
    st.markdown("### 📉 Debt-to-Income (DTI) Analysis")
    if enable_stress:
        st.info(
            f"Active Scenario: **{scenario_name}** | "
            f"Rate Shock: +{stress_rate_val}% | Income Shock: -{stress_inc_val}%"
        )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Monthly Obligation</div>"
            f"<div class='metric-value'>Rs.{df_dti_res['Obligation'].sum():,.0f}</div>"
            f"</div>", unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Aggregate Coverage</div>"
            f"<div class='metric-value'>{dti_agg_dti:.2f}x</div>"
            f"</div>", unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Effective Income</div>"
            f"<div class='metric-value'>Rs.{eff_income:,.0f}</div>"
            f"</div>", unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Income Shortfall</div>"
            f"<div class='metric-value'>Rs.{dti_shortfall:,.0f}</div>"
            f"</div>", unsafe_allow_html=True
        )

    if dti_overall_pass:
        st.markdown(
            "<div class='status-banner status-pass'>✅ DTI REQUEST APPROVED</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='status-banner status-fail'>⚠️ DTI PORTFOLIO DECLINED</div>",
            unsafe_allow_html=True
        )

    disp_dti           = df_dti_res.copy()
    disp_dti['Status'] = disp_dti['Pass_Status'].apply(lambda x: "✅ PASS" if x else "❌ FAIL")
    st.dataframe(
        disp_dti[[
            'Loan Type', 'Amount', 'Effective_Rate', 'Obligation',
            'Available_Income_Snapshot', 'Actual Coverage', 'Required Multiplier', 'Status'
        ]],
        hide_index=True, use_container_width=True
    )

    st.markdown("---")

    # ── LTV Display ──────────────────────────────────────────────────
    st.markdown("### 🏠 Loan-to-Value (LTV) Analysis")
    k5, k6, k7, k8 = st.columns(4)
    with k5:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Total Exposure</div>"
            f"<div class='metric-value'>Rs.{ltv_summary['total_exposure']:,.0f}</div>"
            f"</div>", unsafe_allow_html=True
        )
    with k6:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Total FMV</div>"
            f"<div class='metric-value'>Rs.{ltv_summary['total_fmv']:,.0f}</div>"
            f"</div>", unsafe_allow_html=True
        )
    with k7:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Weighted LTV</div>"
            f"<div class='metric-value'>{ltv_summary['wtd_ltv']:.2f}%</div>"
            f"</div>", unsafe_allow_html=True
        )
    with k8:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-label'>Aggregate LTV</div>"
            f"<div class='metric-value'>{ltv_summary['aggregate_ltv']:.2f}%</div>"
            f"</div>", unsafe_allow_html=True
        )

    if ltv_overall_pass:
        st.markdown(
            "<div class='status-banner status-pass'>✅ LTV PORTFOLIO APPROVED</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='status-banner status-fail'>⚠️ LTV PORTFOLIO DECLINED</div>",
            unsafe_allow_html=True
        )

    disp_ltv = []
    for r in ltv_results:
        is_unsec = r.get('Is_Unsecured', False)
        ltv_val  = r.get('LTV%')
        max_ltv  = r.get('Max LTV%')

        if is_unsec:
            ltv_disp = "EXEMPT"
        elif r.get('No_FMV_Error'):
            ltv_disp = "NO FMV"
        elif ltv_val is None:
            ltv_disp = "N/A"
        else:
            ltv_disp = f"{ltv_val:.2f}%"

        disp_ltv.append({
            "ID":        r.get('loan_account_id'),
            "Facility":  r['Loan Type'],
            "Principal": f"Rs. {r['Principal']:,.0f}",
            "Total FMV": "N/A" if is_unsec else f"Rs. {r['Total FMV']:,.0f}",
            "LTV%":      ltv_disp,
            "Max LTV%":  "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%",
            "Status":    "✅ PASS" if r['Pass_Status'] else "❌ FAIL"
        })
    st.dataframe(pd.DataFrame(disp_ltv), hide_index=True, use_container_width=True)

    st.markdown("---")

    # ── PDF Export ───────────────────────────────────────────────────
    st.markdown("### 📄 Generate Continuous Report")
    ec1, ec2, ec3 = st.columns([2, 1, 1])
    with ec1:
        report_name = st.text_input(
            "Client / Portfolio Name",
            placeholder="e.g. John Doe - Q1 Review",
            label_visibility="collapsed"
        )
    with ec2:
        report_type = st.selectbox(
            "Report Scope", ["Integrated (Both)", "DTI Only", "LTV Only"]
        )
    with ec3:
        if st.button("🚀 Generate PDF", type="primary", use_container_width=True):
            if not report_name.strip():
                st.error("Enter a client name.")
            else:
                with st.spinner("Generating document…"):
                    r_type = (
                        'Integrated' if 'Integrated' in report_type
                        else ('DTI' if 'DTI' in report_type else 'LTV')
                    )
                    payload = {
                        'gross_income':     gross_income,
                        'eff_income':       eff_income,
                        'scenario_name':    scenario_name,
                        'stress_rate':      stress_rate_val,
                        'stress_inc':       stress_inc_val,
                        'enable_stress':    enable_stress,
                        'dti_overall_pass': dti_overall_pass,
                        'dti_agg_dti':      dti_agg_dti,
                        'dti_shortfall':    dti_shortfall,
                        'df_dti_res':       df_dti_res if r_type in ['DTI', 'Integrated'] else None,
                        'ltv_results':      ltv_results if r_type in ['LTV', 'Integrated'] else [],
                        'ltv_summary':      ltv_summary if r_type in ['LTV', 'Integrated'] else {},
                        'income_sources':   (st.session_state.income_sources
                                             if inc_mode == "Multiple Sources" else []),
                        'fmv_sources':      st.session_state.fmv_sources
                    }
                    try:
                        pdf_bytes = generate_integrated_pdf(report_name.strip(), payload)
                        if not pdf_bytes or len(pdf_bytes) == 0:
                            st.error("PDF generation returned empty content. Check server logs.")
                        else:
                            st.session_state['generated_pdf'] = pdf_bytes
                            st.session_state['generated_pdf_name'] = (
                                f"{r_type}_Report_"
                                f"{report_name.strip().replace(' ', '_')}_"
                                f"{datetime.now().strftime('%Y%m%d')}.pdf"
                            )
                            st.rerun()
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
                        st.code(traceback.format_exc(), language="python")

    if 'generated_pdf' in st.session_state and st.session_state['generated_pdf']:
        pdf_data = st.session_state['generated_pdf']
        st.success(f"✅ Report ready — {len(pdf_data):,} bytes")
        st.download_button(
            label="⬇️ Download PDF Now",
            data=pdf_data,
            file_name=st.session_state['generated_pdf_name'],
            mime="application/pdf",
            type="secondary",
            use_container_width=True
        )

else:
    st.info(
        "👋 Add facilities using the form above to begin analysis. "
        "Ensure Income and Collateral configurations are set in the sidebar."
    )
