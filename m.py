Here is the complete, updated Streamlit application code with the requested PDF modifications applied:

```python
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import copy
import os
import io
import tempfile
import traceback

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Integrated DTI & LTV Analysis Engine",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# ==========================================
# AUTHENTICATION
# ==========================================
def _check_credentials(username: str, password: str) -> bool:
    try:
        return (username == st.secrets["auth"]["username"] and
                password == st.secrets["auth"]["password"])
    except Exception:
        return (username == "admin" and password == "admin")


def login_ui():
    st.markdown("""
    <style>
    [data-testid="stSidebar"]       { display: none !important; }
    #MainMenu, footer, header       { visibility: hidden !important; }
    .stApp {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 40%, #312e81 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stAppViewContainer"] > section > div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        padding: 2rem 1rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        padding: 0 !important;
        gap: 0 !important;
    }
    [data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
        background: #ffffff !important;
        border-radius: 20px !important;
        border: 1px solid rgba(99,102,241,0.12) !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3), 0 4px 6px rgba(0,0,0,0.05) !important;
        padding: 0 !important;
        overflow: hidden !important;
        max-width: 460px !important;
        margin: 0 auto !important;
    }
    .login-header {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 55%, #7c3aed 100%);
        padding: 2.8rem 2rem 2.2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .login-header::before {
        content: '';
        position: absolute; top: -50%; left: -30%;
        width: 160%; height: 200%;
        background: radial-gradient(ellipse, rgba(255,255,255,0.10) 0%, transparent 60%);
        pointer-events: none;
    }
    .login-header .logo-icon { font-size: 3rem; display: block; margin-bottom: 0.8rem; position: relative; z-index: 1; }
    .login-header .app-title { font-size: 1.55rem; font-weight: 800; color: #fff; letter-spacing: -0.03em; margin-bottom: 0.35rem; position: relative; z-index: 1; }
    .login-header .app-sub { font-size: 0.78rem; color: rgba(255,255,255,0.72); font-weight: 600; text-transform: uppercase; letter-spacing: 0.14em; position: relative; z-index: 1; }
    .login-body-area { padding: 2rem 2.2rem 1rem; }
    .login-body-area .welcome-title { font-size: 1.25rem; font-weight: 700; color: #1e1b4b; margin-bottom: 0.3rem; }
    .login-body-area .welcome-sub { font-size: 0.88rem; color: #64748b; line-height: 1.55; margin-bottom: 1.4rem; }
    .field-label { display: block; font-size: 0.8rem; font-weight: 600; color: #374151; margin-bottom: 0.35rem; margin-top: 1.1rem; }
    div[data-testid="stTextInput"] > div > div {
        background: #f9fafb !important; border: 1.5px solid #e5e7eb !important;
        border-radius: 10px !important; transition: all 0.2s ease;
    }
    div[data-testid="stTextInput"] > div > div:focus-within {
        border-color: #7c3aed !important; background: #fff !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.10) !important;
    }
    div[data-testid="stTextInput"] > div > div > input {
        background: transparent !important; border: none !important;
        color: #111827 !important; font-size: 0.95rem !important; padding: 0.75rem 0.9rem !important;
    }
    div[data-testid="stTextInput"] > div > div > input::placeholder { color: #9ca3af !important; }
    div[data-testid="stTextInput"] label { display: none !important; }
    div.stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #4338ca 0%, #7c3aed 100%) !important;
        color: #fff !important; border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; font-size: 1rem !important;
        padding: 0.8rem 1.5rem !important; margin-top: 1.6rem !important;
        box-shadow: 0 4px 14px rgba(124,58,237,0.30) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(124,58,237,0.40) !important; }
    .login-error-box {
        background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px;
        padding: 0.7rem 0.9rem; margin-top: 1rem; font-size: 0.82rem;
        color: #b91c1c; font-weight: 500; display: flex; gap: 0.5rem; align-items: flex-start;
    }
    .login-footer { text-align: center; padding: 1rem 2rem 1.4rem; font-size: 0.72rem; color: #94a3b8; border-top: 1px solid #f1f5f9; }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    _sp_l, col_card, _sp_r = st.columns([1, 2.2, 1])
    with col_card:
        st.markdown("""
        <div class="login-header">
            <span class="logo-icon">🏦</span>
            <div class="app-title">Integrated Analysis Engine</div>
            <div class="app-sub">DTI &amp; LTV Credit Assessment Platform</div>
        </div>
        <div class="login-body-area">
            <div class="welcome-title">Welcome Back</div>
            <div class="welcome-sub">Sign in with your institutional credentials to access the integrated credit analysis platform.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="field-label">Username</span>', unsafe_allow_html=True)
        username = st.text_input(
            "u",
            placeholder="Enter your username",
            key="_login_u",
            label_visibility="collapsed",
            autocomplete="username"
        )

        st.markdown('<span class="field-label">Password</span>', unsafe_allow_html=True)
        password = st.text_input(
            "p",
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
                '<div class="login-error-box"><span>⚠️</span><span>{}</span></div>'.format(err),
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="login-footer">Secured connection · Institutional use only · v2.4.1</div>',
            unsafe_allow_html=True
        )

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
            st.session_state["_login_error"] = 'Invalid credentials for "{}". Please check and try again.'.format(u)
            st.rerun()


# ==========================================
# AUTH GATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_username" not in st.session_state:
    st.session_state["auth_username"] = ""

if not st.session_state["authenticated"]:
    login_ui()
    st.stop()

# ==========================================
# GLOBAL STYLES
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
* { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
.stApp {
    background: linear-gradient(145deg, #f0f4ff 0%, #faf5ff 50%, #ede9fe 100%) !important;
    font-family: 'Inter', sans-serif !important; color: #1a1f36;
}
.block-container { max-width: 96% !important; padding-top: 1.5rem !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%); box-shadow: 4px 0 24px rgba(0,0,0,0.18); }
[data-testid="stSidebar"] * { color: #e0e7ff; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
[data-testid="stSidebar"] input { background: rgba(255,255,255,0.95) !important; color: #1e1b4b !important; font-weight: 600; border-radius: 8px; }
[data-testid="stSidebar"] .stRadio > div { background: rgba(255,255,255,0.95) !important; border-radius: 8px; padding: 0.5rem !important; margin: 0.5rem 0 !important; }
[data-testid="stSidebar"] .stRadio label { color: #1e1b4b !important; font-weight: 600 !important; font-size: 0.9rem !important; }
[data-testid="stSidebar"] .stRadio input[type="radio"] { accent-color: #7c3aed !important; }
[data-testid="stSidebar"] .stExpander { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; margin-bottom: 1rem; overflow: hidden; }
[data-testid="stSidebar"] .stExpander summary { color: #fff !important; font-weight: 700 !important; font-size: 1rem !important; padding: 0.8rem 1rem !important; background: rgba(255,255,255,0.08); }
[data-testid="stSidebar"] .stExpander .streamlit-expanderContent { padding: 1rem !important; }
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
    border-radius: 10px !important; border: 1px solid #e2e8f0 !important;
    padding: 0.65rem 0.9rem !important; font-size: 0.95rem !important; background: #f8fafc !important; transition: all 0.2s;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {
    border-color: #7c3aed !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important; background: white !important;
}
div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {
    background-color: #7c3aed !important; border-color: #7c3aed !important; color: white !important;
    border-radius: 8px; font-weight: 600; transition: all 0.2s ease;
}
div.stButton > button[kind="primary"]:hover { background-color: #6d28d9 !important; transform: translateY(-1px); }
.metric-card { background: linear-gradient(135deg, #fff 0%, #f5f3ff 100%); padding: 1.25rem 1.5rem; border-radius: 14px; border: 1px solid #ddd6fe; box-shadow: 0 4px 14px rgba(124,58,237,0.08); }
.metric-label { font-size: 0.75rem; font-weight: 700; color: #7c3aed; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem; }
.metric-value { font-size: 1.7rem; font-weight: 700; color: #1e1b4b; font-family: 'DM Mono', monospace; line-height: 1.1; }
.status-banner { padding: 0.9rem 1.5rem; border-radius: 12px; font-weight: 700; font-size: 1rem; text-align: center; margin: 1.25rem 0; }
.status-pass { background: #d1fae5; border: 2px solid #059669; color: #065f46; }
.status-fail { background: #fee2e2; border: 2px solid #dc2626; color: #991b1b; }
.input-section { background: white; padding: 2rem; border-radius: 16px; border-left: 4px solid #7c3aed; box-shadow: 0 8px 32px rgba(0,0,0,0.05); margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# POLICY DATA
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
# STATE
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
# LTV / DTI HELPERS
# ==========================================
def get_policy_dict():
    return {p["Loan Type"]: (None if p["Unsecured"] else p["Max LTV%"]) for p in st.session_state.ltv_policy}

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
    return "{}{:03d}".format(prefix, st.session_state.loan_type_counters[prefix])

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
    has_assigned = (loan.get('collateral_mode') == 'assigned' and bool(loan.get('assigned_collateral_ids')))
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
    remaining_fmv = {sid: collateral_fmv_map[sid] for sid in fmv_id_set}
    effective_fmv_denom = {}

    active_loans = [
        l for l in loans
        if not _loan_is_ltv_exempt(l)
        and policy.get(l['Loan Type']) is not None
        and (l.get('collateral_mode', 'pool') == 'pool'
             or (l.get('collateral_mode') == 'assigned' and bool(l.get('assigned_collateral_ids'))))
    ]

    for loan in active_loans:
        lid = loan['_loan_id']
        mode = loan.get('collateral_mode', 'pool')
        max_ltv = policy.get(loan['Loan Type'])
        allowed_ids = vehicle_ids if _is_hp_loan(loan['Loan Type']) else property_ids

        if mode == 'pool':
            total_remaining = sum(remaining_fmv[cid] for cid in allowed_ids)
            effective_fmv_denom[lid] = total_remaining
            if total_remaining > 0 and max_ltv:
                req_fmv = loan['Principal'] / (max_ltv / 100.0)
                consumed = min(req_fmv, total_remaining)
                for cid in allowed_ids:
                    proportion = remaining_fmv[cid] / total_remaining
                    remaining_fmv[cid] = max(0.0, remaining_fmv[cid] - consumed * proportion)
        else:
            cids = [c for c in loan.get('assigned_collateral_ids', []) if c in fmv_id_set and c in allowed_ids]
            available = sum(remaining_fmv.get(cid, 0.0) for cid in cids)
            effective_fmv_denom[lid] = available
            if available > 0 and max_ltv:
                req_fmv = loan['Principal'] / (max_ltv / 100.0)
                consumed = min(req_fmv, available)
                for cid in cids:
                    proportion = remaining_fmv[cid] / available
                    remaining_fmv[cid] = max(0.0, remaining_fmv[cid] - consumed * proportion)

    results = []
    for loan in loans:
        lid = loan['_loan_id']
        lt = loan['Loan Type']
        principal = loan['Principal']
        mode = loan.get('collateral_mode', 'pool')
        exempt = _loan_is_ltv_exempt(loan)
        max_ltv = policy.get(lt)

        exempt_reason = None
        if max_ltv is None:
            exempt_reason = "policy"
        elif loan.get('override_ltv', False):
            exempt_reason = "override"
        elif loan.get('tied_property_ids') and not (mode == 'assigned' and bool(loan.get('assigned_collateral_ids'))):
            exempt_reason = "tieup"

        if exempt:
            results.append({
                **loan,
                'Max LTV%': None,
                'Assigned FMV': 0.0,
                'Pool FMV': 0.0,
                'Total FMV': 0.0,
                'LTV%': None,
                'Pass_Status': True,
                'Is_Unsecured': True,
                'Collateral_Mode': mode,
                'No_FMV_Error': False,
                'Exempt_Reason': exempt_reason
            })
            continue

        fmv_denom = effective_fmv_denom.get(lid, 0.0)
        if mode == 'pool':
            assigned_fmv_val, pool_fmv_val, total_alloc = 0.0, fmv_denom, fmv_denom
        else:
            assigned_fmv_val, pool_fmv_val, total_alloc = fmv_denom, 0.0, fmv_denom

        if total_alloc <= 0:
            ltv_pct, passes, no_fmv_error = None, False, True
        else:
            ltv_pct = principal / total_alloc * 100.0
            passes = ltv_pct <= max_ltv
            no_fmv_error = False

        results.append({
            **loan,
            'Max LTV%': max_ltv,
            'Assigned FMV': assigned_fmv_val,
            'Pool FMV': pool_fmv_val,
            'Total FMV': total_alloc,
            'LTV%': ltv_pct,
            'Pass_Status': passes,
            'Is_Unsecured': False,
            'Collateral_Mode': mode,
            'No_FMV_Error': no_fmv_error,
            'Exempt_Reason': None
        })

    secured_results = [r for r in results if not r['Is_Unsecured']]
    total_secured_principal = sum(r['Principal'] for r in secured_results)
    total_exposure = sum(r['Principal'] for r in results)
    total_alloc_fmv_sum = sum(r['Total FMV'] for r in secured_results)

    wtd_ltv = (total_secured_principal / total_alloc_fmv_sum * 100.0 if total_alloc_fmv_sum > 0 else 0.0)
    aggregate_ltv = (total_secured_principal / total_fmv_original * 100.0 if total_fmv_original > 0 else 0.0)
    overall_pass = all(r['Pass_Status'] for r in results)

    return results, {
        'total_fmv': total_fmv_original,
        'total_exposure': total_exposure,
        'total_secured_principal': total_secured_principal,
        'total_alloc_fmv': total_alloc_fmv_sum,
        'wtd_ltv': wtd_ltv,
        'aggregate_ltv': aggregate_ltv,
        'overall_pass': overall_pass
    }

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
            return (principal * r_monthly * ((1 + r_monthly) ** n_months)) / (((1 + r_monthly) ** n_months) - 1)
        except Exception:
            return 0.0

def run_waterfall_allocation(df, total_income):
    df_sorted = df.sort_values(by='Required Multiplier', ascending=False).reset_index(drop=True)
    run_inc = total_income
    pass_flags, act_covs, snaps = [], [], []
    num_loans = len(df_sorted)

    for idx, row in df_sorted.iterrows():
        obl = row['Obligation']
        req_mult = row['Required Multiplier']
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

    df_sorted['Pass_Status'] = pass_flags
    df_sorted['Actual Coverage'] = act_covs
    df_sorted['Available_Income_Snapshot'] = snaps
    return df_sorted

# ==========================================
# PDF HELPERS
# ==========================================
def _pdf_safe_text(value):
    try:
        return str(value).encode('latin-1', 'ignore').decode('latin-1')
    except Exception:
        return ""


def _pdf_extract_bytes(pdf) -> bytes:
    errors = []

    # Strategy 1
    try:
        result = pdf.output()
        if result is not None:
            data = bytes(result)
            if len(data) > 0:
                return data
            errors.append("Strategy 1: output() returned {} bytes".format(len(data)))
        else:
            errors.append("Strategy 1: output() returned None")
    except Exception as e:
        errors.append("Strategy 1 failed: {}: {}".format(type(e).__name__, e))

    # Strategy 2
    try:
        result = pdf.output(dest='S')
        if result is not None:
            if isinstance(result, (bytes, bytearray)):
                data = bytes(result)
            elif isinstance(result, str):
                data = result.encode('latin-1')
            else:
                data = bytes(result)
            if len(data) > 0:
                return data
            errors.append("Strategy 2: dest='S' returned {} bytes".format(len(data)))
        else:
            errors.append("Strategy 2: dest='S' returned None")
    except Exception as e:
        errors.append("Strategy 2 failed: {}: {}".format(type(e).__name__, e))

    # Strategy 3
    tmp_path = None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(tmp_fd)
        try:
            pdf.output(tmp_path)
        except TypeError:
            try:
                pdf.output(name=tmp_path, dest='F')
            except TypeError:
                pdf.output(dest='F', name=tmp_path)

        with open(tmp_path, 'rb') as f:
            data = f.read()

        if len(data) > 0:
            return data
        errors.append("Strategy 3: file was {} bytes".format(len(data)))
    except Exception as e:
        errors.append("Strategy 3 failed: {}: {}".format(type(e).__name__, e))
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    # Strategy 4
    try:
        buf = io.BytesIO()
        pdf.output(buf)
        data = buf.getvalue()
        if len(data) > 0:
            return data
        errors.append("Strategy 4: buffer was {} bytes".format(len(data)))
    except Exception as e:
        errors.append("Strategy 4 failed: {}: {}".format(type(e).__name__, e))

    raise RuntimeError(
        "PDF output extraction failed. All strategies exhausted:\n" +
        "\n".join("  - " + e for e in errors)
    )


class ReportPDF(FPDF):
    def __init__(self, client_name='', report_id='', generated_by=''):
        super(ReportPDF, self).__init__(orientation='P', unit='mm', format='A4')
        self.client_name = _pdf_safe_text(client_name)
        self.report_id = _pdf_safe_text(report_id)
        self.generated_by = _pdf_safe_text(generated_by)
        self.date_str = datetime.now().strftime("%B %d, %Y")

        self.set_left_margin(10)
        self.set_right_margin(10)
        self.set_top_margin(12)
        self.set_auto_page_break(auto=True, margin=18)

        try:
            self.alias_nb_pages()
        except Exception:
            pass

    def header(self):
        if self.page_no() == 1:
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(0, 32, 96)
            self.cell(0, 10, 'INTEGRATED CREDIT ANALYSIS REPORT', 0, 1, 'C')

            self.set_font('Helvetica', '', 9)
            self.set_text_color(90, 90, 90)
            self.cell(
                0,
                5,
                'Client: ' + self.client_name + '    |    Date: ' + self.date_str + '    |    Ref: ' + self.report_id,
                0,
                1,
                'C'
            )

            if self.generated_by:
                self.cell(0, 5, 'Generated by: ' + self.generated_by, 0, 1, 'C')

            self.ln(2)
            self.set_draw_color(0, 32, 96)
            self.set_line_width(0.6)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)
        else:
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(0, 32, 96)
            self.cell(95, 5, 'Integrated Credit Analysis Report', 0, 0, 'L')
            self.cell(95, 5, 'Client: ' + self.client_name + ' | ' + self.date_str, 0, 1, 'R')

            self.set_draw_color(180, 190, 210)
            self.set_line_width(0.2)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, 'Confidential - Page ' + str(self.page_no()), 0, 0, 'C')


def generate_integrated_pdf(client_name: str, report_data: dict) -> bytes:
    report_id = _pdf_safe_text(report_data.get('report_id', datetime.now().strftime("%Y%m%d-%H%M%S")))
    generated_by = _pdf_safe_text(report_data.get('generated_by', ''))

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
    income_sources   = report_data.get('income_sources', [])
    fmv_sources      = report_data.get('fmv_sources', [])
    report_scope     = report_data.get('report_scope', 'Integrated')

    include_dti = report_scope in ['DTI', 'Integrated'] and df_dti_res is not None and not df_dti_res.empty
    include_ltv = report_scope in ['LTV', 'Integrated'] and bool(ltv_results)

    total_fmv = ltv_summary.get('total_fmv', 0) if include_ltv else 0
    aggregate_ltv = ltv_summary.get('aggregate_ltv', 0) if include_ltv else None
    wtd_ltv = ltv_summary.get('wtd_ltv', 0) if include_ltv else None

    if include_ltv:
        total_exposure = ltv_summary.get('total_exposure', 0)
    elif include_dti:
        total_exposure = df_dti_res['Amount'].sum()
    else:
        total_exposure = 0

    ltv_overall_pass = ltv_summary.get('overall_pass', True) if include_ltv else True

    overall_pass = True
    if include_dti:
        overall_pass = overall_pass and dti_overall_pass
    if include_ltv:
        overall_pass = overall_pass and ltv_overall_pass

    pdf = ReportPDF(client_name=client_name, report_id=report_id, generated_by=generated_by)

    # Internal helpers
    def _ensure_space(needed):
        if pdf.get_y() + needed > pdf.h - 22:
            pdf.add_page()

    def _section(title):
        _ensure_space(18)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 32, 96)
        pdf.set_fill_color(235, 240, 250)
        pdf.cell(0, 8, '  ' + _pdf_safe_text(title), 0, 1, 'L', True)
        pdf.ln(3)

    def _note(text):
        _ensure_space(10)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, 5, _pdf_safe_text(text), 0, 1, 'L')
        pdf.ln(2)

    def _status_banner(text, ok):
        _ensure_space(14)
        if ok:
            pdf.set_fill_color(5, 150, 105)
        else:
            pdf.set_fill_color(220, 38, 38)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 9, _pdf_safe_text(text), 0, 1, 'C', True)
        pdf.ln(3)

    def _summary_table(rows):
        w = [48, 47, 48, 47]
        for row in rows:
            _ensure_space(8)
            values = row['values']
            colors = row.get('value_colors', {})

            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(0, 32, 96)
            pdf.set_fill_color(238, 242, 250)
            pdf.cell(w[0], 6, _pdf_safe_text(values[0]), 1, 0, 'L', True)

            pdf.set_font('Helvetica', '', 8)
            if 1 in colors:
                c = colors[1]
                pdf.set_text_color(c[0], c[1], c[2])
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.cell(w[1], 6, _pdf_safe_text(values[1]), 1, 0, 'R', False)

            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(0, 32, 96)
            pdf.set_fill_color(238, 242, 250)
            pdf.cell(w[2], 6, _pdf_safe_text(values[2]), 1, 0, 'L', True)

            pdf.set_font('Helvetica', '', 8)
            if 3 in colors:
                c = colors[3]
                pdf.set_text_color(c[0], c[1], c[2])
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.cell(w[3], 6, _pdf_safe_text(values[3]), 1, 1, 'R', False)

    def render_table(widths, headers, rows, aligns=None, row_h=6, font_size=7, header_size=7, zebra=True):
        if aligns is None:
            aligns = ['L'] + ['R'] * (len(widths) - 1)

        def _header():
            pdf.set_font('Helvetica', 'B', header_size)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(0, 32, 96)
            for i, h in enumerate(headers):
                pdf.cell(widths[i], 7, _pdf_safe_text(h), 1, 0, aligns[i], True)
            pdf.ln(7)

        _ensure_space(20)
        _header()

        for idx, row in enumerate(rows):
            if pdf.get_y() + row_h > pdf.h - 22:
                pdf.add_page()
                _header()

            values = row.get('values', [])
            bold = row.get('bold', False)
            fill = row.get('fill', False)
            fill_color = row.get('fill_color', (245, 247, 250))
            cell_colors = row.get('cell_colors', {})
            span_first = row.get('span_first', 0)

            if zebra and not bold and not fill and idx % 2 == 1:
                fill = True
                fill_color = (245, 247, 250)

            if fill:
                pdf.set_fill_color(fill_color[0], fill_color[1], fill_color[2])

            pdf.set_font('Helvetica', 'B' if bold else '', font_size)

            if span_first and span_first > 1 and len(values) > 0:
                if 0 in cell_colors:
                    c = cell_colors[0]
                    pdf.set_text_color(c[0], c[1], c[2])
                else:
                    pdf.set_text_color(0, 0, 0)

                span_w = sum(widths[:span_first])
                pdf.cell(span_w, row_h, _pdf_safe_text(values[0]), 1, 0, aligns[0], fill)

                for vi in range(1, len(values)):
                    col_idx = span_first + vi - 1
                    if col_idx >= len(widths):
                        break

                    if col_idx in cell_colors:
                        c = cell_colors[col_idx]
                        pdf.set_text_color(c[0], c[1], c[2])
                    else:
                        pdf.set_text_color(0, 0, 0)

                    al = aligns[col_idx] if col_idx < len(aligns) else 'R'
                    pdf.cell(widths[col_idx], row_h, _pdf_safe_text(values[vi]), 1, 0, al, fill)

                pdf.ln(row_h)
            else:
                for i, val in enumerate(values):
                    if i >= len(widths):
                        break

                    if i in cell_colors:
                        c = cell_colors[i]
                        pdf.set_text_color(c[0], c[1], c[2])
                    else:
                        pdf.set_text_color(0, 0, 0)

                    al = aligns[i] if i < len(aligns) else 'R'
                    pdf.cell(widths[i], row_h, _pdf_safe_text(val), 1, 0, al, fill)

                pdf.ln(row_h)

    def money(x):
        try:
            return "Rs. {:,.2f}".format(float(x))
        except Exception:
            return "N/A"

    def money0(x):
        try:
            return "{:,.0f}".format(float(x))
        except Exception:
            return "0"

    def pct(x):
        if x is None:
            return "N/A"
        try:
            return "{:.2f}%".format(float(x))
        except Exception:
            return "N/A"

    # ===== PAGE 1: EXEC SUMMARY =====
    pdf.add_page()

    _section('Executive Summary')

    if overall_pass:
        _status_banner('OVERALL ASSESSMENT:  APPROVED', True)
    else:
        _status_banner('OVERALL ASSESSMENT:  DECLINED', False)

    scope_label = {
        'Integrated': 'Integrated (DTI + LTV)',
        'DTI': 'DTI Only',
        'LTV': 'LTV Only'
    }.get(report_scope, 'Integrated')

    _note('Report Scope: {}  |  Stress Testing: {}'.format(
        scope_label,
        'Enabled' if enable_stress else 'Disabled'
    ))

    dti_coverage_txt = "{:.2f}x".format(dti_agg_dti) if include_dti else "N/A"
    shortfall_txt = money(dti_shortfall) if include_dti else "N/A"
    dti_status_txt = ('PASS' if dti_overall_pass else 'FAIL') if include_dti else "N/A"
    ltv_status_txt = ('PASS' if ltv_overall_pass else 'FAIL') if include_ltv else "N/A"
    total_fmv_txt = money(total_fmv) if include_ltv else "N/A"
    aggregate_ltv_txt = pct(aggregate_ltv) if include_ltv else "N/A"
    wtd_ltv_txt = pct(wtd_ltv) if include_ltv else "N/A"

    green = (5, 150, 105)
    red = (220, 38, 38)

    dti_color = green if dti_overall_pass else red
    ltv_color = green if ltv_overall_pass else red

    if not include_dti:
        dti_color = (0, 0, 0)
    if not include_ltv:
        ltv_color = (0, 0, 0)

    eff_label = "Effective Income (Post-Stress)" if (enable_stress and include_dti) else "Effective Income (Baseline)"

    _summary_table([
        {
            'values': [
                'Monthly Gross Income', money(gross_income),
                eff_label, money(eff_income)
            ]
        },
        {
            'values': [
                'Total Loan Exposure', money(total_exposure),
                'Total Collateral FMV', total_fmv_txt
            ]
        },
        {
            'values': [
                'Aggregate DTI Coverage', dti_coverage_txt,
                'Aggregate LTV%', aggregate_ltv_txt
            ]
        },
        {
            'values': [
                'DTI Status', dti_status_txt,
                'LTV Status', ltv_status_txt
            ],
            'value_colors': {
                1: dti_color,
                3: ltv_color
            }
        },
        {
            'values': [
                'DTI Income Shortfall', shortfall_txt,
                'Weighted LTV', wtd_ltv_txt
            ]
        }
    ])

    pdf.ln(3)

    # ===== DTI SECTION =====
    if include_dti:
        _section('Debt-to-Income (DTI) Analysis')

        if enable_stress:
            stress_rows = [
                {
                    'values': [
                        _pdf_safe_text(scenario_name),
                        "+{:.2f}%".format(stress_rate),
                        "-{:.2f}%".format(stress_inc),
                        money(eff_income)
                    ]
                }
            ]
            render_table(
                [70, 40, 40, 40],
                ['Scenario', 'Rate Shock', 'Income Shock', 'Effective Income'],
                stress_rows,
                aligns=['L', 'C', 'C', 'R'],
                row_h=6,
                font_size=8,
                header_size=8,
                zebra=False
            )
            pdf.ln(3)

        # Income sources
        income_rows = []
        if income_sources:
            for src in income_sources:
                income_rows.append({
                    'values': [
                        _pdf_safe_text(src.get('Source', '')),
                        money(src.get('Amount', 0))
                    ]
                })
        else:
            income_rows.append({
                'values': ['Monthly Gross Income', money(gross_income)]
            })

        income_rows.append({
            'values': ['Total Gross Income', money(gross_income)],
            'bold': True,
            'fill': True,
            'fill_color': (226, 232, 243)
        })

        render_table(
            [120, 70],
            ['Income Source', 'Amount (Rs.)'],
            income_rows,
            aligns=['L', 'R'],
            row_h=6,
            font_size=8,
            header_size=8
        )

        pdf.ln(4)

        # DTI waterfall
        dti_rows = []
        for _, row in df_dti_res.iterrows():
            status = "PASS" if bool(row['Pass_Status']) else "FAIL"
            status_color = green if bool(row['Pass_Status']) else red

            dti_rows.append({
                'values': [
                    _pdf_safe_text(row['Loan Type']),
                    money0(row['Amount']),
                    money0(row['Obligation']),
                    money0(row['Available_Income_Snapshot']),
                    "{:.2f}x".format(row['Actual Coverage']),
                    "{:.2f}x".format(row['Required Multiplier']),
                    status
                ],
                'cell_colors': {6: status_color}
            })

        render_table(
            [48, 26, 26, 28, 20, 20, 22],
            ['Facility Type', 'Principal', 'Payment', 'Rem. Income', 'Act. Cov.', 'Req. Cov.', 'Status'],
            dti_rows,
            aligns=['L', 'R', 'R', 'R', 'R', 'R', 'C'],
            row_h=6,
            font_size=7,
            header_size=7
        )

        pdf.ln(3)

    # ===== LTV SECTION =====
    if include_ltv:
        _section('Loan-to-Value (LTV) Analysis')

        if fmv_sources:
            coll_rows = []
            for src in fmv_sources:
                ctype = "Vehicle" if src.get('IsVehicle') else "Property"
                coll_rows.append({
                    'values': [
                        _pdf_safe_text(src.get('Plot', 'N/A')),
                        _pdf_safe_text(src.get('Owner', 'N/A')),
                        ctype,
                        money0(src.get('Amount', 0))
                    ]
                })

            coll_rows.append({
                'values': ['', '', 'Total FMV', money0(total_fmv)],
                'bold': True,
                'fill': True,
                'fill_color': (226, 232, 243)
            })

            render_table(
                [60, 45, 25, 60],
                ['Property Reference', 'Owner', 'Type', 'FMV (Rs.)'],
                coll_rows,
                aligns=['L', 'L', 'C', 'R'],
                row_h=6,
                font_size=8,
                header_size=8
            )

            pdf.ln(4)
        else:
            _note('No collateral / FMV sources recorded.')

        ltv_rows = []
        for row in ltv_results:
            is_unsec = row.get('Is_Unsecured', False)
            ltv_val = row.get('LTV%')
            max_ltv = row.get('Max LTV%')

            if is_unsec:
                ltv_text = "EXEMPT"
                max_disp = "N/A"
            elif row.get('No_FMV_Error'):
                ltv_text = "NO FMV"
                max_disp = "{:.0f}%".format(max_ltv) if max_ltv else "N/A"
            else:
                ltv_text = "{:.2f}%".format(ltv_val) if ltv_val is not None else "N/A"
                max_disp = "{:.0f}%".format(max_ltv) if max_ltv else "N/A"

            status = "PASS" if row['Pass_Status'] else "FAIL"
            fmv_disp = 'N/A' if is_unsec else money0(row['Total FMV'])
            status_color = green if row['Pass_Status'] else red

            ltv_rows.append({
                'values': [
                    _pdf_safe_text(row.get('loan_account_id', 'N/A')),
                    _pdf_safe_text(row['Loan Type']),
                    money0(row['Principal']),
                    fmv_disp,
                    ltv_text,
                    max_disp,
                    status
                ],
                'cell_colors': {6: status_color}
            })

        agg_status = 'PASS' if ltv_overall_pass else 'FAIL'
        agg_color = green if ltv_overall_pass else red

        ltv_rows.append({
            'values': [
                'AGGREGATE PORTFOLIO TOTAL',
                money0(total_exposure),
                money0(total_fmv),
                pct(aggregate_ltv),
                'N/A',
                agg_status
            ],
            'span_first': 2,
            'bold': True,
            'fill': True,
            'fill_color': (226, 232, 243),
            'cell_colors': {6: agg_color}
        })

        render_table(
            [22, 46, 28, 28, 22, 22, 22],
            ['A/C No.', 'Facility Type', 'Principal', 'Total FMV', 'LTV%', 'Max LTV%', 'Status'],
            ltv_rows,
            aligns=['L', 'L', 'R', 'R', 'R', 'R', 'C'],
            row_h=6,
            font_size=7,
            header_size=7
        )

        pdf.ln(3)

        # ===== COLLATERAL NOTES (NEW) =====
        # Notes for LTV Exempt (Override), Property Tie-up, and Dedicated Collateral Assignment
        collateral_notes = []

        fmv_lookup = {s['id']: s for s in fmv_sources if 'id' in s}

        def _plot_labels(ids):
            labels = []
            for cid in ids:
                s = fmv_lookup.get(cid)
                if s:
                    labels.append("{} (Rs.{:,.0f})".format(s.get('Plot', 'N/A'), s.get('Amount', 0)))
            return ", ".join(labels) if labels else "None"

        for row in ltv_results:
            lid = row.get('loan_account_id', 'N/A')
            lt = row.get('Loan Type', '')
            mode = row.get('Collateral_Mode', 'pool')
            exempt_reason = row.get('Exempt_Reason')
            tied_ids = row.get('tied_property_ids', []) or []
            assigned_ids = row.get('assigned_collateral_ids', []) or []

            if exempt_reason == 'override':
                collateral_notes.append(
                    "[{}] {} - LTV Exempt: Override collateral requirement applied; treated as unsecured for LTV purposes.".format(lid, lt)
                )
            elif exempt_reason == 'tieup':
                tied_str = _plot_labels(tied_ids)
                collateral_notes.append(
                    "[{}] {} - LTV Exempt: Property tie-up applied as additional security [{}].".format(lid, lt, tied_str)
                )

            if mode == 'assigned' and assigned_ids:
                assigned_str = _plot_labels(assigned_ids)
                collateral_notes.append(
                    "[{}] {} - Dedicated collateral assigned: {}.".format(lid, lt, assigned_str)
                )

            # Also note tie-up explicitly when loan is NOT exempt via tie-up (i.e., collateral still required but tie-up added)
            if exempt_reason != 'tieup' and tied_ids and not exempt_reason:
                tied_str = _plot_labels(tied_ids)
                collateral_notes.append(
                    "[{}] {} - Property tie-up as additional security [{}].".format(lid, lt, tied_str)
                )

        if collateral_notes:
            _ensure_space(12 + len(collateral_notes) * 6)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(0, 32, 96)
            pdf.set_fill_color(235, 240, 250)
            pdf.cell(0, 7, '  Collateral Notes', 0, 1, 'L', True)
            pdf.ln(2)

            pdf.set_font('Helvetica', '', 7.5)
            pdf.set_text_color(60, 60, 60)
            for note in collateral_notes:
                pdf.multi_cell(0, 4, _pdf_safe_text("  - " + note))
            pdf.ln(3)

    # ===== (Notes & Disclaimer section removed) =====

    if pdf.page < 1:
        raise RuntimeError("PDF has no pages - content rendering failed.")

    return _pdf_extract_bytes(pdf)


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Configuration Panel")

    with st.expander("💰 Income & Stress Configuration (DTI)", expanded=True):
        inc_mode = st.radio("Income Entry Method", ["Single Total", "Multiple Sources"])
        gross_income = 0.0

        if inc_mode == "Single Total":
            gross_income = st.number_input("Monthly Gross Income (Rs.)", value=150000.0, step=5000.0)
        else:
            c1, c2 = st.columns([1.5, 1])
            src = c1.text_input("Income Source")
            amt = c2.number_input("Amount (Rs.)", min_value=0.0)
            if st.button("➕ Add Source", type="primary"):
                if src.strip() and amt > 0:
                    st.session_state.income_sources.append({"Source": src.strip(), "Amount": amt})
                    st.rerun()

            if st.session_state.income_sources:
                st.dataframe(pd.DataFrame(st.session_state.income_sources), hide_index=True)
                if st.button("Clear All Sources"):
                    st.session_state.income_sources = []
                    st.rerun()
                gross_income = sum(x['Amount'] for x in st.session_state.income_sources)

        st.markdown("---")
        enable_stress = st.toggle("Enable Stress Testing", value=False)
        stress_rate_val, stress_inc_val = 0.0, 0.0
        scenario_name = "Baseline (No Stress)"
        stressed_sources_selection = []

        if enable_stress:
            if inc_mode == "Multiple Sources" and st.session_state.income_sources:
                all_src = [x['Source'] for x in st.session_state.income_sources]
                stressed_sources_selection = st.multiselect("Select Sources to Stress", all_src, default=all_src)

            with st.form("create_scenario_form"):
                fc1, fc2 = st.columns(2)
                c_name = fc1.text_input("Scenario Name")
                c_rate = fc2.number_input("Rate Shock (+%)", 0.0, 50.0, 2.0, step=0.5)
                c_inc = st.number_input("Income Reduction (-%)", 0.0, 100.0, 10.0, step=5.0)
                if st.form_submit_button("Save Scenario", type="primary"):
                    if c_name:
                        st.session_state.custom_scenarios.append({"Name": c_name, "Rate": c_rate, "Income": c_inc})
                        st.rerun()

            if st.session_state.custom_scenarios:
                c_names = [s['Name'] for s in st.session_state.custom_scenarios]
                active_c_name = st.selectbox("Active Scenario", c_names)
                active_s = next((s for s in st.session_state.custom_scenarios if s['Name'] == active_c_name), None)
                if active_s:
                    stress_rate_val = active_s['Rate']
                    stress_inc_val = active_s['Income']
                    scenario_name = active_c_name

    with st.expander("🏠 Collateral Configuration (LTV)", expanded=True):
        sb_plot = st.text_input("Property Reference", placeholder="e.g. Plot 42-B")
        sb_owner = st.text_input("Owner Name", placeholder="e.g. John Doe")
        sb_fmv = st.number_input("Fair Market Value (Rs.)", min_value=0.0, step=50000.0)
        sb_coll_type = st.radio("Collateral Type", ["Property", "Vehicle"])

        if st.button("Add Property", type="primary"):
            if sb_fmv > 0 and sb_plot.strip():
                st.session_state.fmv_sources.append({
                    "id": _next_fmv_id(),
                    "Plot": sb_plot.strip(),
                    "Owner": sb_owner.strip(),
                    "Amount": sb_fmv,
                    "IsVehicle": (sb_coll_type == "Vehicle")
                })
                st.rerun()

        if st.session_state.fmv_sources:
            st.markdown("**Total FMV:** Rs. {:,.0f}".format(sum(s['Amount'] for s in st.session_state.fmv_sources)))
            for src in st.session_state.fmv_sources:
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    tag = "🚗 " if src.get('IsVehicle') else "🏠 "
                    st.markdown("{} **{}** — Rs. {:,.0f}".format(tag, src['Plot'], src['Amount']))
                with col_b:
                    if st.button("X", key="del_fmv_{}".format(src['id'])):
                        st.session_state.fmv_sources = [s for s in st.session_state.fmv_sources if s['id'] != src['id']]
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
# MAIN DASHBOARD
# ==========================================
st.title("🏦 Integrated DTI & LTV Analysis Engine")
st.markdown("Unified credit assessment for Debt-to-Income and Loan-to-Value metrics.")

with st.container():
    st.markdown("<div class='input-section'><h5>➕ Add New Facility</h5>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
    with c1:
        l_type = st.selectbox("Facility Type", list(LOAN_CONFIG.keys()))
    with c2:
        l_amt = st.number_input("Principal Amount (Rs.)", step=10000.0, min_value=0.0)
    with c3:
        l_rate = st.number_input("Interest Rate (%)", value=12.0, step=0.25)
    with c4:
        l_ten = st.number_input("Tenure (Years)", value=DEFAULT_TENURE.get(l_type, 5), min_value=1)

    st.markdown("#### DTI Parameters")
    c_opt, c_btn = st.columns([3, 1])
    with c_opt:
        use_man = st.checkbox("Use Fixed Monthly Payment (Override EMI)")
    man_emi = st.number_input("Fixed Monthly Payment (Rs.)", 0.0, step=1000.0) if use_man else 0.0

    st.markdown("#### LTV Parameters")
    policy_dict = get_policy_dict()
    max_ltv_sel = policy_dict.get(l_type)
    is_hp = _is_hp_loan(l_type)

    override_ltv = False
    coll_mode = "pool"
    selected_colls = []
    tie_up_colls = []

    if max_ltv_sel is not None:
        override_ltv = st.checkbox("Override collateral requirement (LTV Exempt)")
        if not override_ltv:
            use_dedicated = st.checkbox("Assign dedicated collateral?")
            coll_mode = "assigned" if use_dedicated else "pool"
            if use_dedicated:
                eligible = [s for s in st.session_state.fmv_sources if bool(s.get('IsVehicle')) == is_hp]
                if eligible:
                    opts = {"{} - Rs.{:,.0f}".format(s['Plot'], s['Amount']): s['id'] for s in eligible}
                    sel_labels = st.multiselect("Select Collateral(s)", list(opts.keys()))
                    selected_colls = [opts[lbl] for lbl in sel_labels]
                else:
                    st.warning("No {} collateral available.".format('Vehicle' if is_hp else 'Property'))

        use_tie_up = st.checkbox("Tie up Property (additional security)?")
        if use_tie_up and st.session_state.fmv_sources:
            opts = {"{} - Rs.{:,.0f}".format(s['Plot'], s['Amount']): s['id'] for s in st.session_state.fmv_sources}
            tie_sel = st.multiselect("Select properties to tie up", list(opts.keys()))
            tie_up_colls = [opts[lbl] for lbl in tie_sel]
    else:
        st.info("Unsecured facility — no collateral required for LTV.")

    if c_btn.button("Add to Portfolio", type="primary", use_container_width=True):
        errors = []
        if l_amt <= 0:
            errors.append("Principal must be > 0")
        if l_rate <= 0:
            errors.append("Rate must be > 0")
        if l_ten <= 0:
            errors.append("Tenure must be >= 1")
        if use_man and man_emi <= 0:
            errors.append("Fixed EMI must be > 0")

        cap_ok, cap_msg = _check_professional_caps(l_type, l_amt, st.session_state.loans)
        if not cap_ok:
            errors.append(cap_msg)

        if errors:
            for e in errors:
                st.error(e)
        else:
            std_emi = calculate_obligation(l_type, l_amt, l_rate, l_ten)
            lid = st.session_state.loan_id_counter
            st.session_state.loan_id_counter += 1
            ac_id = _generate_loan_account_id(l_type)

            st.session_state.loans.append({
                "Loan Type": l_type,
                "Principal": l_amt,
                "Base Rate": l_rate,
                "Tenure": l_ten,
                "Base_Obligation": man_emi if use_man else std_emi,
                "Required Multiplier": LOAN_CONFIG[l_type],
                "Is_Manual": use_man,
                "_loan_id": lid,
                "loan_account_id": ac_id,
                "collateral_mode": coll_mode,
                "assigned_collateral_ids": selected_colls,
                "tied_property_ids": tie_up_colls,
                "override_ltv": override_ltv
            })
            st.success("✅ Added [{}] {}".format(ac_id, l_type))
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# RESULTS
# ==========================================
if st.session_state.loans:
    eff_income = gross_income
    if enable_stress:
        if inc_mode == "Multiple Sources" and stressed_sources_selection:
            var_inc = sum(x['Amount'] for x in st.session_state.income_sources if x['Source'] in stressed_sources_selection)
            fix_inc = gross_income - var_inc
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
    total_obl = df_dti_res['Obligation'].sum()
    dti_agg_dti = eff_income / total_obl if total_obl > 0 else 0

    dti_shortfall = 0.0
    if not dti_overall_pass:
        req_ideal = sum(r['Obligation'] * r['Required Multiplier'] for _, r in df_dti_res.iterrows())
        dti_shortfall = max(0, req_ideal - eff_income)

    ltv_results, ltv_summary = run_portfolio_ltv(st.session_state.loans, st.session_state.fmv_sources)
    ltv_overall_pass = ltv_summary['overall_pass']

    # DTI UI
    st.markdown("### 📉 Debt-to-Income (DTI) Analysis")
    if enable_stress:
        st.info("Active Scenario: **{}** | Rate Shock: +{}% | Income Shock: -{}%".format(
            scenario_name, stress_rate_val, stress_inc_val
        ))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Monthly Obligation</div><div class='metric-value'>Rs.{:,.0f}</div></div>".format(
                df_dti_res['Obligation'].sum()
            ),
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Aggregate Coverage</div><div class='metric-value'>{:.2f}x</div></div>".format(
                dti_agg_dti
            ),
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Effective Income</div><div class='metric-value'>Rs.{:,.0f}</div></div>".format(
                eff_income
            ),
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Income Shortfall</div><div class='metric-value'>Rs.{:,.0f}</div></div>".format(
                dti_shortfall
            ),
            unsafe_allow_html=True
        )

    if dti_overall_pass:
        st.markdown("<div class='status-banner status-pass'>✅ DTI REQUEST APPROVED</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-banner status-fail'>⚠️ DTI PORTFOLIO DECLINED</div>", unsafe_allow_html=True)

    disp_dti = df_dti_res.copy()
    disp_dti['Status'] = disp_dti['Pass_Status'].apply(lambda x: "✅ PASS" if x else "❌ FAIL")
    st.dataframe(
        disp_dti[[
            'Loan Type', 'Amount', 'Effective_Rate', 'Obligation',
            'Available_Income_Snapshot', 'Actual Coverage', 'Required Multiplier', 'Status'
        ]],
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # LTV UI
    st.markdown("### 🏠 Loan-to-Value (LTV) Analysis")
    k5, k6, k7, k8 = st.columns(4)
    with k5:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Total Exposure</div><div class='metric-value'>Rs.{:,.0f}</div></div>".format(
                ltv_summary['total_exposure']
            ),
            unsafe_allow_html=True
        )
    with k6:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Total FMV</div><div class='metric-value'>Rs.{:,.0f}</div></div>".format(
                ltv_summary['total_fmv']
            ),
            unsafe_allow_html=True
        )
    with k7:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Weighted LTV</div><div class='metric-value'>{:.2f}%</div></div>".format(
                ltv_summary['wtd_ltv']
            ),
            unsafe_allow_html=True
        )
    with k8:
        st.markdown(
            "<div class='metric-card'><div class='metric-label'>Aggregate LTV</div><div class='metric-value'>{:.2f}%</div></div>".format(
                ltv_summary['aggregate_ltv']
            ),
            unsafe_allow_html=True
        )

    if ltv_overall_pass:
        st.markdown("<div class='status-banner status-pass'>✅ LTV PORTFOLIO APPROVED</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-banner status-fail'>⚠️ LTV PORTFOLIO DECLINED</div>", unsafe_allow_html=True)

    disp_ltv = []
    for r in ltv_results:
        is_unsec = r.get('Is_Unsecured', False)
        ltv_val = r.get('LTV%')
        max_ltv = r.get('Max LTV%')

        if is_unsec:
            ltv_disp = "EXEMPT"
        elif r.get('No_FMV_Error'):
            ltv_disp = "NO FMV"
        elif ltv_val is None:
            ltv_disp = "N/A"
        else:
            ltv_disp = "{:.2f}%".format(ltv_val)

        disp_ltv.append({
            "ID": r.get('loan_account_id'),
            "Facility": r['Loan Type'],
            "Principal": "Rs. {:,.0f}".format(r['Principal']),
            "Total FMV": "N/A" if is_unsec else "Rs. {:,.0f}".format(r['Total FMV']),
            "LTV%": ltv_disp,
            "Max LTV%": "N/A" if (is_unsec or max_ltv is None) else "{:.0f}%".format(max_ltv),
            "Status": "✅ PASS" if r['Pass_Status'] else "❌ FAIL"
        })

    st.dataframe(pd.DataFrame(disp_ltv), hide_index=True, use_container_width=True)

    st.markdown("---")

    # PDF EXPORT
    st.markdown("### 📄 Generate Report")
    ec1, ec2, ec3 = st.columns([2, 1, 1])

    with ec1:
        report_name = st.text_input(
            "Client / Portfolio Name",
            placeholder="e.g. John Doe - Q1 Review",
            label_visibility="collapsed"
        )

    with ec2:
        report_type = st.selectbox(
            "Report Scope",
            ["Integrated (Both)", "DTI Only", "LTV Only"]
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
                        'gross_income': gross_income,
                        'eff_income': eff_income,
                        'scenario_name': scenario_name,
                        'stress_rate': stress_rate_val,
                        'stress_inc': stress_inc_val,
                        'enable_stress': enable_stress,
                        'dti_overall_pass': dti_overall_pass,
                        'dti_agg_dti': dti_agg_dti,
                        'dti_shortfall': dti_shortfall,
                        'df_dti_res': df_dti_res if r_type in ['DTI', 'Integrated'] else None,
                        'ltv_results': ltv_results if r_type in ['LTV', 'Integrated'] else [],
                        'ltv_summary': ltv_summary if r_type in ['LTV', 'Integrated'] else {},
                        'income_sources': (st.session_state.income_sources if inc_mode == "Multiple Sources" else []),
                        'fmv_sources': st.session_state.fmv_sources,
                        'report_scope': r_type,
                        'generated_by': st.session_state.get('auth_username', ''),
                        'report_id': datetime.now().strftime("%Y%m%d-%H%M%S")
                    }

                    try:
                        pdf_bytes = generate_integrated_pdf(report_name.strip(), payload)
                        if pdf_bytes and len(pdf_bytes) > 100:
                            st.session_state['generated_pdf'] = pdf_bytes
                            st.session_state['generated_pdf_name'] = "{}_Report_{}_{}.pdf".format(
                                r_type,
                                report_name.strip().replace(' ', '_'),
                                datetime.now().strftime('%Y%m%d')
                            )
                            st.rerun()
                        else:
                            st.error("PDF generation produced invalid output ({} bytes).".format(
                                len(pdf_bytes) if pdf_bytes else 0
                            ))
                    except Exception as e:
                        st.error("PDF generation failed: {}".format(e))
                        st.code(traceback.format_exc(), language="python")

    if 'generated_pdf' in st.session_state and st.session_state['generated_pdf']:
        pdf_data = st.session_state['generated_pdf']
        st.success("✅ Report ready — {:,} bytes".format(len(pdf_data)))
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_data,
            file_name=st.session_state['generated_pdf_name'],
            mime="application/pdf",
            use_container_width=True
        )

else:
    st.info(
        "👋 Add facilities using the form above to begin analysis. "
        "Ensure Income and Collateral configurations are set in the sidebar."
    )
```
