import streamlit as st
import pandas as pd
from weasyprint import HTML
from html import escape as esc
from datetime import datetime
import copy
import time

# ==========================================
# 🔐 AUTHENTICATION SYSTEM (DTI Style)
# ==========================================
def _check_credentials(username: str, password: str) -> bool:
    try:
        return (username == st.secrets["auth"]["username"] and 
                password == st.secrets["auth"]["password"])
    except Exception:
        return (username == "admin" and password == "admin")

def login_ui():
    st.markdown("<style>[data-testid=\"stSidebar\"] { display: none; }</style>", unsafe_allow_html=True)
    cols = st.columns([1, 1.2, 1])
    with cols[1]:
        st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
        with st.container():
            st.markdown("""
            <div class='login-container'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>🏦</div>
            <div class='login-header'>Welcome Back</div>
            <div class='login-sub'>Sign in to access the Integrated Analysis Engine</div>
            </div>
            """, unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("Sign In", type="primary", width='stretch')
            if submit:
                try:
                    if _check_credentials(username, password):
                        st.session_state['authenticated'] = True
                        st.success("Access Granted")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception:
                    st.error("Secrets not configured correctly")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login_ui()
    st.stop()

# ==========================================
# 🎨 PAGE CONFIG & GLOBAL STYLES
# ==========================================
st.set_page_config(
    page_title="Integrated DTI & LTV Analysis Engine",
    layout="wide",
    page_icon="",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1a1f36;
    letter-spacing: -0.01em;
}
.block-container { max-width: 95% !important; }
.main { background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%); }

.login-container {
    background: white; padding: 3rem; border-radius: 24px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.08); text-align: center;
    border: 1px solid #e2e8f0;
}
.login-header { font-size: 1.75rem; font-weight: 800; margin-bottom: 0.5rem; color: #0f172a; }
.login-sub { color: #64748b; font-size: 0.95rem; margin-bottom: 2rem; }

div[data-testid="stTextInput"] input {
    border-radius: 12px !important; border: 1px solid #e2e8f0 !important;
    padding: 1rem !important; font-size: 1rem !important;
    background: #f8fafc !important; transition: all 0.2s;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 4px rgba(124,58,237,0.1) !important;
    background: white !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    box-shadow: 4px 0 24px rgba(0,0,0,0.12);
}
[data-testid="stSidebar"] * { color: #f1f5f9; }
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background: rgba(255,255,255,0.95) !important;
    color: #334155 !important; font-weight: 600;
}

div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
    background-color: #7c3aed !important; border-color: #7c3aed !important;
    color: white !important; border-radius: 8px; font-weight: 600;
    transition: all 0.3s ease;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {
    background-color: #6d28d9 !important; border-color: #6d28d9 !important;
}

.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    padding: 1.5rem; border-radius: 16px; border: 1px solid #e2e8f0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.metric-value { font-size: 2rem; font-weight: 800; color: #0f172a; font-family: 'JetBrains Mono', monospace; }
.metric-delta-positive { color: #10b981; font-weight: 700; font-size: 0.9rem; }
.metric-delta-negative { color: #ef4444; font-weight: 700; font-size: 0.9rem; }

.status-banner {
    padding: 1rem 1.5rem; border-radius: 12px; font-weight: 700;
    font-size: 1rem; text-align: center; margin: 1.5rem 0;
}
.status-banner-pass { background: #d1fae5; border: 2px solid #10b981; color: #065f46; }
.status-banner-fail { background: #fee2e2; border: 2px solid #ef4444; color: #991b1b; }

.input-section {
    background: white; padding: 2rem; border-radius: 16px;
    border-left: 4px solid #7c3aed;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08); margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
#  POLICY DATA & CONFIGURATIONS
# ==========================================
LOAN_CONFIG = {
    "Personal Term Loan (PTL)": 2.0, "Personal OD": 2.0, "Share Loan": 2.0,
    "Mortgage Loan": 2.0, "Auto Loan": 2.0, "Home Loan": 1.428,
    "First Time Home Buyer": 1.25, "Education Loan": 2.0,
    "Professional OD": 2.0, "Professional T/L": 2.0,
    "HP Loan": 2.0, "HP Loan Commercial": 2.0, "HP Loan (Used)": 2.0, "HP Loan Commercial-EV": 2.0,
    "Cash Credit facility": 2.0, "Short Term Facility": 2.0, "Permanent WC Loan": 2.0, "Business Term Loan": 2.0
}
DEFAULT_TENURE = {
    "Personal OD": 1, "Home Loan": 15, "First Time Home Buyer": 20,
    "Share Loan": 1, "Professional OD": 1, "Professional T/L": 5
}

DEFAULT_LTV_POLICY = [
    {"Loan Type": "Home Loan", "Max LTV%": 60.0, "Unsecured": False},
    {"Loan Type": "Mortgage Loan", "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "HP Loan", "Max LTV%": 60.0, "Unsecured": False},
    {"Loan Type": "HP Loan Commercial", "Max LTV%": 80.0, "Unsecured": False},
    {"Loan Type": "HP Loan (Used)", "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "HP Loan Commercial-EV", "Max LTV%": 80.0, "Unsecured": False},
    {"Loan Type": "First Time Home Buyer", "Max LTV%": 80.0, "Unsecured": False},
    {"Loan Type": "Personal Term Loan (PTL)", "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "Education Loan", "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "Professional T/L", "Max LTV%": None, "Unsecured": False},
    {"Loan Type": "Professional OD", "Max LTV%": None, "Unsecured": False},
    {"Loan Type": "Cash Credit facility", "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Short Term Facility", "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Permanent WC Loan", "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Business Term Loan", "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Personal OD", "Max LTV%": 50.0, "Unsecured": False},
]

LOAN_TYPE_PREFIXES = {
    "Home Loan": "HL", "Mortgage Loan": "ML", "HP Loan": "HP",
    "HP Loan Commercial": "HPC", "HP Loan (Used)": "HPU",
    "HP Loan Commercial-EV": "HPEV", "First Time Home Buyer": "FTB",
    "Personal Term Loan (PTL)": "PTL", "Education Loan": "EDL",
    "Professional T/L": "PRTL", "Professional OD": "PROD",
    "Cash Credit facility": "CC", "Short Term Facility": "STF",
    "Permanent WC Loan": "PWC", "Business Term Loan": "BTL", "Personal OD": "POD",
    "Auto Loan": "AL", "Share Loan": "SL"
}

HP_FACILITY_TYPES = {"HP Loan", "HP Loan Commercial", "HP Loan (Used)", "HP Loan Commercial-EV"}
PROFESSIONAL_OD_CAP = 500_000.0
PROFESSIONAL_TL_CAP = 1_500_000.0
PROFESSIONAL_COMBINED_CAP = 1_500_000.0

# ==========================================
# 🏠 APP STATE INITIALIZATION
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
#  HELPER & LTV ENGINE FUNCTIONS
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
    return f"{prefix}{st.session_state.loan_type_counters[prefix]:03d}"

def _check_professional_caps(l_type, l_amt, existing_loans):
    if l_type not in ("Professional OD", "Professional T/L"): return True, ""
    existing_od = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional OD")
    existing_tl = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional T/L")
    new_od = existing_od + (l_amt if l_type == "Professional OD" else 0.0)
    new_tl = existing_tl + (l_amt if l_type == "Professional T/L" else 0.0)
    if l_type == "Professional OD" and new_od > PROFESSIONAL_OD_CAP:
        return False, f"Professional OD total exceeds cap."
    if l_type == "Professional T/L" and new_tl > PROFESSIONAL_TL_CAP:
        return False, f"Professional T/L total exceeds cap."
    if (new_od + new_tl) > PROFESSIONAL_COMBINED_CAP:
        return False, f"Combined Prof OD + T/L exceeds combined cap."
    return True, ""

def _loan_is_ltv_exempt(loan: dict) -> bool:
    policy = get_policy_dict()
    if policy.get(loan.get('Loan Type')) is None: return True
    if loan.get('override_ltv', False): return True
    has_assigned = loan.get('collateral_mode') == 'assigned' and bool(loan.get('assigned_collateral_ids'))
    if loan.get('tied_property_ids') and not has_assigned: return True
    return False

def run_portfolio_ltv(loans, fmv_sources):
    policy = get_policy_dict()
    fmv_sources = [s for s in fmv_sources if 'id' in s]
    fmv_id_set = {s['id'] for s in fmv_sources}
    
    vehicle_ids = {s['id'] for s in fmv_sources if s.get('IsVehicle')}
    property_ids = fmv_id_set - vehicle_ids
    collateral_fmv_map = {s['id']: s['Amount'] for s in fmv_sources}
    total_fmv_original = sum(s['Amount'] for s in fmv_sources)
    
    remaining_fmv = {sid: collateral_fmv_map[sid] for sid in fmv_id_set}
    effective_fmv_denom = {}
    
    active_loans = [
        l for l in loans if not _loan_is_ltv_exempt(l) and policy.get(l['Loan Type']) is not None
        and (l.get('collateral_mode', 'pool') == 'pool' or (l.get('collateral_mode') == 'assigned' and bool(l.get('assigned_collateral_ids'))))
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
        if max_ltv is None: exempt_reason = "policy"
        elif loan.get('override_ltv', False): exempt_reason = "override"
        elif loan.get('tied_property_ids') and not (mode == 'assigned' and bool(loan.get('assigned_collateral_ids'))):
            exempt_reason = "tieup"
            
        if exempt:
            results.append({**loan, 'Max LTV%': None, 'Assigned FMV': 0.0, 'Pool FMV': 0.0,
                'Total FMV': 0.0, 'LTV%': None, 'Pass_Status': True, 'Is_Unsecured': True, 
                'Collateral_Mode': mode, 'No_FMV_Error': False, 'Exempt_Reason': exempt_reason})
            continue
            
        fmv_denom = effective_fmv_denom.get(lid, 0.0)
        if mode == 'pool':
            assigned_fmv_val = 0.0; pool_fmv_val = fmv_denom; total_alloc = fmv_denom
        else:
            assigned_fmv_val = fmv_denom; pool_fmv_val = 0.0; total_alloc = fmv_denom
            
        if total_alloc <= 0:
            ltv_pct = None; passes = False; no_fmv_error = True
        else:
            ltv_pct = principal / total_alloc * 100.0
            passes = ltv_pct <= max_ltv; no_fmv_error = False
            
        results.append({**loan, 'Max LTV%': max_ltv, 'Assigned FMV': assigned_fmv_val, 
            'Pool FMV': pool_fmv_val, 'Total FMV': total_alloc, 'LTV%': ltv_pct,
            'Pass_Status': passes, 'Is_Unsecured': False, 'Collateral_Mode': mode, 
            'No_FMV_Error': no_fmv_error, 'Exempt_Reason': None})

    secured_results = [r for r in results if not r['Is_Unsecured']]
    total_secured_principal = sum(r['Principal'] for r in secured_results)
    total_exposure = sum(r['Principal'] for r in results)
    total_alloc_fmv_sum = sum(r['Total FMV'] for r in secured_results)
    
    wtd_ltv = total_secured_principal / total_alloc_fmv_sum * 100.0 if total_alloc_fmv_sum > 0 else 0.0
    aggregate_ltv = total_secured_principal / total_fmv_original * 100.0 if total_fmv_original > 0 else 0.0
    overall_pass = all(r['Pass_Status'] for r in results)

    return results, {
        'total_fmv': total_fmv_original, 'total_exposure': total_exposure,
        'total_secured_principal': total_secured_principal, 'total_alloc_fmv': total_alloc_fmv_sum,
        'wtd_ltv': wtd_ltv, 'aggregate_ltv': aggregate_ltv, 'overall_pass': overall_pass
    }

# ==========================================
#  DTI ENGINE
# ==========================================
def calculate_obligation(loan_type, principal, rate, tenure):
    if principal <= 0 or rate <= 0: return 0.0
    r_monthly = (rate / 100) / 12
    if "OD" in loan_type or "Overdraft" in loan_type:
        return principal * r_monthly
    else:
        if tenure <= 0: return 0.0
        n_months = tenure * 12
        try:
            return (principal * r_monthly * ((1 + r_monthly) ** n_months)) / (((1 + r_monthly) ** n_months) - 1)
        except:
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
        is_last_loan = (idx == num_loans - 1)
        if not is_last_loan:
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
# 📄 CONTINUOUS PROFESSIONAL PDF ENGINE
# ==========================================
_PDF_CSS = """
@page { 
    size: A4; 
    margin: 16mm 14mm 18mm 14mm; 
    @bottom-left { content: "Integrated Credit Analysis"; font-size: 7.5pt; color: #666; }
    @bottom-center { content: "Page " counter(page) " of " counter(pages); font-size: 7.5pt; color: #666; }
    @bottom-right { content: "DATE_STR"; font-size: 7.5pt; color: #666; }
}
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 9pt; color: #1a1a1a; line-height: 1.4; }
h1 { font-size: 18pt; margin: 0 0 4px 0; text-transform: uppercase; color: #002060; letter-spacing: 0.5px; border-bottom: 2.5px solid #7c3aed; padding-bottom: 6px;}
h2 { font-size: 12pt; margin: 20px 0 10px 0; color: #4338ca; text-transform: uppercase; letter-spacing: 0.3px; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 4px; page-break-after: avoid; }
h3 { font-size: 10pt; margin: 14px 0 6px 0; color: #1e1b4b; text-transform: uppercase; letter-spacing: 0.2px; page-break-after: avoid; }
.header-table { width: 100%; margin-bottom: 16px; }
.header-table td { vertical-align: top; font-size: 9.5pt; }
.summary-box { border: 1px solid #cbd5e1; padding: 12px 16px; margin-bottom: 16px; background: #f8fafc; border-radius: 4px; page-break-inside: avoid; }
.status-line { font-weight: bold; font-size: 10pt; margin-bottom: 10px; padding: 6px 10px; border-radius: 4px; }
.status-pass { color: #065f46; background: #d1fae5; border: 1px solid #a7f3d0; }
.status-fail { color: #991b1b; background: #fee2e2; border: 1px solid #fecaca; }
.kv-table { width: 100%; font-size: 9pt; border-collapse: collapse; }
.kv-table td { padding: 3px 0; } 
.kv-table td.kv-value { text-align: right; font-weight: bold; font-family: monospace; }
table.data-table { width: 100%; border-collapse: collapse; margin-bottom: 16px; table-layout: fixed; page-break-inside: auto; }
table.data-table tr { page-break-inside: avoid; page-break-after: auto; }
table.data-table thead { display: table-header-group; }
table.data-table th, table.data-table td { padding: 6px 8px; text-align: left; vertical-align: middle; font-size: 8.5pt; }
table.data-table th { border-top: 1.5px solid #000; border-bottom: 1.5px solid #000; font-weight: bold; text-transform: uppercase; background: #f1f5f9; font-size: 7.5pt; letter-spacing: 0.3px; }
table.data-table td { border-bottom: 0.75px solid #e2e8f0; }
table.data-table tbody tr:nth-child(even) td { background: #f8fafc; }
table.data-table tr.aggregate-row td { border-top: 1.5px solid #000; border-bottom: 1.5px solid #000; font-weight: bold; background: #e2e8f0 !important; }
.right { text-align: right !important; } .center { text-align: center !important; }
.pass { color: #059669; font-weight: bold; } .fail { color: #dc2626; font-weight: bold; }
.exempt { color: #d97706; font-weight: bold; } .muted { color: #64748b; }
"""

def generate_integrated_pdf(client_name, report_data):
    date_str = datetime.now().strftime("%B %d, %Y")
    
    gross_income = report_data.get('gross_income', 0)
    eff_income = report_data.get('eff_income', 0)
    scenario_name = report_data.get('scenario_name', 'Baseline')
    stress_rate = report_data.get('stress_rate', 0)
    stress_inc = report_data.get('stress_inc', 0)
    enable_stress = report_data.get('enable_stress', False)
    dti_overall_pass = report_data.get('dti_overall_pass', True)
    dti_agg_dti = report_data.get('dti_agg_dti', 0)
    dti_shortfall = report_data.get('dti_shortfall', 0)
    df_dti_res = report_data.get('df_dti_res')
    
    ltv_results = report_data.get('ltv_results', [])
    ltv_summary = report_data.get('ltv_summary', {})
    total_fmv = ltv_summary.get('total_fmv', 0)
    total_exposure = ltv_summary.get('total_exposure', 0)
    aggregate_ltv = ltv_summary.get('aggregate_ltv', 0)
    ltv_overall_pass = ltv_summary.get('overall_pass', True)
    
    income_sources = report_data.get('income_sources', [])
    fmv_sources = report_data.get('fmv_sources', [])
    
    overall_status_pass = dti_overall_pass and ltv_overall_pass
    status_class = "status-pass" if overall_status_pass else "status-fail"
    status_text = "OVERALL ASSESSMENT: APPROVED" if overall_status_pass else "OVERALL ASSESSMENT: DECLINED"

    html = []
    html.append('<!DOCTYPE html><html><head><meta charset="UTF-8"><style>')
    html.append(_PDF_CSS.replace('DATE_STR', date_str))
    html.append('</style></head><body>')
    
    html.append('<h1>Integrated Credit Analysis Report</h1>')
    html.append('<table class="header-table"><tr>')
    html.append(f'<td><strong>Client Name:</strong> {esc(client_name)}</td>')
    html.append(f'<td class="right"><strong>Analysis Date:</strong> {date_str}</td>')
    html.append('</tr></table>')
    
    html.append('<h2>Executive Summary</h2>')
    html.append('<div class="summary-box">')
    html.append(f'<div class="status-line {status_class}">{status_text}</div>')
    html.append('<table class="kv-table">')
    html.append(f'<tr><td>Monthly Gross Income:</td><td class="kv-value">Rs. {gross_income:,.2f}</td>')
    html.append(f'<td style="width:20px"></td><td>Total Loan Exposure:</td><td class="kv-value">Rs. {total_exposure:,.2f}</td></tr>')
    
    if enable_stress:
        html.append(f'<tr><td>Effective Income (Post-Stress):</td><td class="kv-value">Rs. {eff_income:,.2f}</td>')
    else:
        html.append(f'<tr><td>Effective Income (Baseline):</td><td class="kv-value">Rs. {eff_income:,.2f}</td>')
    html.append(f'<td></td><td>Total Collateral FMV:</td><td class="kv-value">Rs. {total_fmv:,.2f}</td></tr>')
    
    html.append(f'<tr><td>Aggregate DTI Coverage:</td><td class="kv-value">{dti_agg_dti:.2f}x</td>')
    html.append(f'<td></td><td>Aggregate LTV%:</td><td class="kv-value">{aggregate_ltv:.2f}%</td></tr>')
    
    dti_status_color = '#059669' if dti_overall_pass else '#dc2626'
    dti_status_text = 'PASS' if dti_overall_pass else 'FAIL'
    html.append(f'<tr><td>DTI Income Shortfall:</td><td class="kv-value">Rs. {dti_shortfall:,.2f}</td>')
    html.append(f'<td></td><td>DTI Status:</td><td class="kv-value" style="color:{dti_status_color}">{dti_status_text}</td></tr>')
    html.append('</table></div>')
    
    # DTI Section
    if df_dti_res is not None and not df_dti_res.empty:
        html.append('<h2>Debt-to-Income (DTI) Analysis</h2>')
        html.append('<h3>Scenario & Income Details</h3>')
        html.append('<table class="kv-table" style="width: 60%; margin-bottom: 16px;">')
        html.append(f'<tr><td>Active Scenario:</td><td class="kv-value">{esc(scenario_name)}</td></tr>')
        if enable_stress:
            html.append(f'<tr><td>Interest Rate Shock:</td><td class="kv-value">+{stress_rate:.2f}%</td></tr>')
            html.append(f'<tr><td>Income Reduction:</td><td class="kv-value">-{stress_inc:.2f}%</td></tr>')
        html.append('</table>')
        
        if income_sources:
            html.append('<h3>Income Sources</h3>')
            html.append('<table class="data-table" style="width: 50%;"><thead><tr><th>Source</th><th class="right">Amount (Rs.)</th></tr></thead><tbody>')
            for src in income_sources:
                html.append(f"<tr><td>{esc(src['Source'])}</td><td class='right'>{src['Amount']:,.2f}</td></tr>")
            html.append(f"<tr class='aggregate-row'><td>Total</td><td class='right'>{gross_income:,.2f}</td></tr></tbody></table>")

        html.append('<h3>Priority Allocation Breakdown</h3>')
        html.append('<table class="data-table"><thead><tr>')
        html.append('<th style="width:22%">Facility Type</th>')
        html.append('<th class="right" style="width:12%">Principal</th>')
        html.append('<th class="right" style="width:12%">Payment</th>')
        html.append('<th class="right" style="width:14%">Rem. Income</th>')
        html.append('<th class="right" style="width:10%">Actual Cov.</th>')
        html.append('<th class="right" style="width:10%">Req. Cov.</th>')
        html.append('<th class="center" style="width:10%">Status</th>')
        html.append('</tr></thead><tbody>')
        
        for _, row in df_dti_res.iterrows():
            status = "PASS" if row['Pass_Status'] else "FAIL"
            s_class = "pass" if row['Pass_Status'] else "fail"
            html.append('<tr>')
            html.append(f'<td>{esc(row["Loan Type"])}</td>')
            html.append(f'<td class="right">{row["Amount"]:,.0f}</td>')
            html.append(f'<td class="right">{row["Obligation"]:,.0f}</td>')
            html.append(f'<td class="right">{row["Available_Income_Snapshot"]:,.0f}</td>')
            html.append(f'<td class="right">{row["Actual Coverage"]:.2f}x</td>')
            html.append(f'<td class="right">{row["Required Multiplier"]:.2f}x</td>')
            html.append(f'<td class="center {s_class}">{status}</td>')
            html.append('</tr>')
        html.append('</tbody></table>')

    # LTV Section
    if ltv_results:
        html.append('<h2>Loan-to-Value (LTV) Analysis</h2>')
        
        if fmv_sources:
            html.append('<h3>Collateral & Fair Market Value Sources</h3>')
            html.append('<table class="data-table"><thead><tr>')
            html.append('<th style="width:30%">Property Reference</th>')
            html.append('<th style="width:20%">Owner</th>')
            html.append('<th style="width:15%">Type</th>')
            html.append('<th class="right" style="width:15%">FMV (Rs.)</th>')
            html.append('</tr></thead><tbody>')
            for src in fmv_sources:
                ctype = "Vehicle" if src.get('IsVehicle') else "Standard"
                html.append('<tr>')
                html.append(f'<td>{esc(src.get("Plot", "N/A"))}</td>')
                html.append(f'<td>{esc(src.get("Owner", "N/A"))}</td>')
                html.append(f'<td>{ctype}</td>')
                html.append(f'<td class="right">{src.get("Amount", 0):,.0f}</td>')
                html.append('</tr>')
            html.append(f'<tr class="aggregate-row"><td colspan="3" class="right">Total FMV</td><td class="right">{total_fmv:,.0f}</td></tr></tbody></table>')

        html.append('<h3>Facility LTV Breakdown</h3>')
        html.append('<table class="data-table"><thead><tr>')
        html.append('<th style="width:10%">A/C No.</th>')
        html.append('<th style="width:20%">Facility Type</th>')
        html.append('<th class="right" style="width:12%">Principal</th>')
        html.append('<th class="right" style="width:12%">Total FMV</th>')
        html.append('<th class="right" style="width:10%">LTV%</th>')
        html.append('<th class="right" style="width:10%">Max LTV%</th>')
        html.append('<th class="center" style="width:10%">Status</th>')
        html.append('</tr></thead><tbody>')
        
        for row in ltv_results:
            is_unsec = row.get('Is_Unsecured', False)
            ltv_val = row.get('LTV%')
            max_ltv = row.get('Max LTV%')
            
            if is_unsec:
                ltv_text, ltv_class = "EXEMPT", "exempt"
                max_disp = "N/A"
            elif row.get('No_FMV_Error'):
                ltv_text, ltv_class = "NO FMV", "fail"
                max_disp = f"{max_ltv:.0f}%" if max_ltv else "N/A"
            else:
                ltv_text = f"{ltv_val:.2f}%"
                ltv_class = "pass" if row['Pass_Status'] else "fail"
                max_disp = f"{max_ltv:.0f}%" if max_ltv else "N/A"
                
            status = "PASS" if row['Pass_Status'] else "FAIL"
            s_class = "pass" if row['Pass_Status'] else "fail"
            
            html.append('<tr>')
            html.append(f'<td>{esc(row.get("loan_account_id", "N/A"))}</td>')
            html.append(f'<td>{esc(row["Loan Type"])}</td>')
            html.append(f'<td class="right">{row["Principal"]:,.0f}</td>')
            fmv_disp = 'N/A' if is_unsec else f"{row['Total FMV']:,.0f}"
            html.append(f'<td class="right">{fmv_disp}</td>')
            html.append(f'<td class="right {ltv_class}">{ltv_text}</td>')
            html.append(f'<td class="right">{max_disp}</td>')
            html.append(f'<td class="center {s_class}">{status}</td>')
            html.append('</tr>')
            
        agg_status_class = 'pass' if ltv_overall_pass else 'fail'
        agg_status_text = 'PASS' if ltv_overall_pass else 'FAIL'
        html.append('<tr class="aggregate-row">')
        html.append('<td colspan="2">AGGREGATE</td>')
        html.append(f'<td class="right">{total_exposure:,.0f}</td>')
        html.append(f'<td class="right">{total_fmv:,.0f}</td>')
        html.append(f'<td class="right">{aggregate_ltv:.2f}%</td>')
        html.append('<td class="right">N/A</td>')
        html.append(f'<td class="center {agg_status_class}">{agg_status_text}</td>')
        html.append('</tr></tbody></table>')

    html.append('</body></html>')
    return HTML(string="".join(html)).write_pdf()

# ==========================================
# 📐 SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.markdown("## ️ Configuration Panel")
    
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
        stress_rate_val, stress_inc_val, scenario_name = 0.0, 0.0, "Baseline (No Stress)"
        stressed_sources_selection = []
        
        if enable_stress:
            if inc_mode == "Multiple Sources" and st.session_state.income_sources:
                all_source_names = [x['Source'] for x in st.session_state.income_sources]
                stressed_sources_selection = st.multiselect("Select Sources to Stress", all_source_names, default=all_source_names)
            
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
                    "id": _next_fmv_id(), "Plot": sb_plot.strip(), "Owner": sb_owner.strip(),
                    "Amount": sb_fmv, "IsVehicle": (sb_coll_type == "Vehicle")
                })
                st.rerun()
                
        if st.session_state.fmv_sources:
            st.markdown(f"**Total FMV:** Rs. {sum(s['Amount'] for s in st.session_state.fmv_sources):,.0f}")
            for src in st.session_state.fmv_sources:
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    v_tag = "🚗 " if src.get('IsVehicle') else "🏠 "
                    st.markdown(f"{v_tag} **{src['Plot']}** - Rs. {src['Amount']:,.0f}")
                with col_b:
                    if st.button("X", key=f"del_fmv_{src['id']}"):
                        st.session_state.fmv_sources = [s for s in st.session_state.fmv_sources if s['id'] != src['id']]
                        for loan in st.session_state.loans:
                            if src['id'] in loan.get('assigned_collateral_ids', []): loan['assigned_collateral_ids'].remove(src['id'])
                            if src['id'] in loan.get('tied_property_ids', []): loan['tied_property_ids'].remove(src['id'])
                        st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset All Data", type="primary", use_container_width=True):
        for k in ['loans', 'income_sources', 'fmv_sources', 'custom_scenarios']: st.session_state[k] = []
        for k in ['loan_id_counter', 'fmv_id_counter']: st.session_state[k] = 0
        st.session_state['loan_type_counters'] = {}
        st.rerun()

# ==========================================
# 🖥️ MAIN DASHBOARD
# ==========================================
st.title(" Integrated DTI & LTV Analysis Engine")
st.markdown("Unified credit assessment for Debt-to-Income and Loan-to-Value metrics.")

with st.container():
    st.markdown("<div class='input-section'><h5>➕ Add New Facility</h5>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([2, 1.5, 1, 1])
    with c1: l_type = st.selectbox("Facility Type", list(LOAN_CONFIG.keys()))
    with c2: l_amt = st.number_input("Principal Amount (Rs.)", step=10000.0, min_value=0.0)
    with c3: l_rate = st.number_input("Interest Rate (%)", value=12.0, step=0.25)
    with c4: l_ten = st.number_input("Tenure (Years)", value=DEFAULT_TENURE.get(l_type, 5), min_value=1)
    
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
                    opts = {f"{s['Plot']} - Rs.{s['Amount']:,.0f}": s['id'] for s in eligible}
                    sel_labels = st.multiselect("Select Collateral(s)", list(opts.keys()))
                    selected_colls = [opts[lbl] for lbl in sel_labels]
                else:
                    st.warning(f"No {'Vehicle' if is_hp else 'Property'} collateral available.")
                    
        use_tie_up = st.checkbox("Tie up Property (additional security)?")
        if use_tie_up and st.session_state.fmv_sources:
            opts = {f"{s['Plot']} - Rs.{s['Amount']:,.0f}": s['id'] for s in st.session_state.fmv_sources}
            tie_sel = st.multiselect("Select properties to tie up", list(opts.keys()))
            tie_up_colls = [opts[lbl] for lbl in tie_sel]
    else:
        st.info("Unsecured facility — no collateral required for LTV.")
        
    if c_btn.button("Add to Portfolio", type="primary", use_container_width=True):
        errors = []
        if l_amt <= 0: errors.append("Principal must be > 0")
        if l_rate <= 0: errors.append("Rate must be > 0")
        if l_ten <= 0: errors.append("Tenure must be >= 1")
        if use_man and man_emi <= 0: errors.append("Fixed EMI must be > 0")
        
        cap_ok, cap_msg = _check_professional_caps(l_type, l_amt, st.session_state.loans)
        if not cap_ok: errors.append(cap_msg)
        
        if errors:
            for e in errors: st.error(e)
        else:
            std_emi = calculate_obligation(l_type, l_amt, l_rate, l_ten)
            lid = st.session_state.loan_id_counter
            st.session_state.loan_id_counter += 1
            ac_id = _generate_loan_account_id(l_type)
            
            st.session_state.loans.append({
                "Loan Type": l_type, "Principal": l_amt, "Base Rate": l_rate, "Tenure": l_ten,
                "Base_Obligation": man_emi if use_man else std_emi, "Required Multiplier": LOAN_CONFIG[l_type],
                "Is_Manual": use_man, "_loan_id": lid, "loan_account_id": ac_id,
                "collateral_mode": coll_mode, "assigned_collateral_ids": selected_colls,
                "tied_property_ids": tie_up_colls, "override_ltv": override_ltv
            })
            st.success(f"✅ Added [{ac_id}] {l_type}")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.loans:
    eff_income = gross_income
    if enable_stress:
        if inc_mode == "Multiple Sources" and stressed_sources_selection:
            var_inc = sum(x['Amount'] for x in st.session_state.income_sources if x['Source'] in stressed_sources_selection)
            fix_inc = gross_income - var_inc
            eff_income = fix_inc + (var_inc * (1.0 - (stress_inc_val / 100.0)))
        else:
            eff_income = gross_income * (1.0 - (stress_inc_val / 100.0))
            
    df_dti = pd.DataFrame(st.session_state.loans)
    df_dti['Amount'] = df_dti['Principal'] 
    
    def get_stress_row(row, s_rate):
        if row['Is_Manual']: return row['Base_Obligation'], row['Base Rate']
        new_r = row['Base Rate'] + s_rate
        return calculate_obligation(row['Loan Type'], row['Amount'], new_r, row['Tenure']), new_r
        
    df_dti[['Obligation', 'Effective_Rate']] = df_dti.apply(lambda x: pd.Series(get_stress_row(x, stress_rate_val)), axis=1)
    df_dti_res = run_waterfall_allocation(df_dti, eff_income)
    
    dti_overall_pass = all(df_dti_res['Pass_Status'])
    dti_agg_dti = eff_income / df_dti_res['Obligation'].sum() if df_dti_res['Obligation'].sum() > 0 else 0
    dti_shortfall = 0.0
    if not dti_overall_pass:
        req_ideal = sum(r['Obligation'] * r['Required Multiplier'] for _, r in df_dti_res.iterrows())
        dti_shortfall = max(0, req_ideal - eff_income)
        
    ltv_results, ltv_summary = run_portfolio_ltv(st.session_state.loans, st.session_state.fmv_sources)
    ltv_overall_pass = ltv_summary['overall_pass']
    
    st.markdown("### 📉 Debt-to-Income (DTI) Analysis")
    if enable_stress:
        st.info(f"Active Scenario: **{scenario_name}** | Rate Shock: +{stress_rate_val}% | Income Shock: -{stress_inc_val}%")
        
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Monthly Obligation</div><div class='metric-value'>Rs.{df_dti_res['Obligation'].sum():,.0f}</div></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='metric-card'><div class='metric-label'>Aggregate Coverage</div><div class='metric-value'>{dti_agg_dti:.2f}x</div></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='metric-card'><div class='metric-label'>Effective Income</div><div class='metric-value'>Rs.{eff_income:,.0f}</div></div>", unsafe_allow_html=True)
    with k4: st.markdown(f"<div class='metric-card'><div class='metric-label'>Income Shortfall</div><div class='metric-value'>Rs.{dti_shortfall:,.0f}</div></div>", unsafe_allow_html=True)
    
    if dti_overall_pass:
        st.markdown("<div class='status-banner status-banner-pass'>✅ DTI REQUEST APPROVED</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-banner status-banner-fail'>⚠️ DTI PORTFOLIO DECLINED</div>", unsafe_allow_html=True)
        
    disp_dti = df_dti_res.copy()
    disp_dti['Status'] = disp_dti['Pass_Status'].apply(lambda x: "✅ PASS" if x else "❌ FAIL")
    st.dataframe(disp_dti[['Loan Type', 'Amount', 'Effective_Rate', 'Obligation', 'Available_Income_Snapshot', 'Actual Coverage', 'Required Multiplier', 'Status']], hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 🏠 Loan-to-Value (LTV) Analysis")
    k5, k6, k7, k8 = st.columns(4)
    with k5: st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Exposure</div><div class='metric-value'>Rs.{ltv_summary['total_exposure']:,.0f}</div></div>", unsafe_allow_html=True)
    with k6: st.markdown(f"<div class='metric-card'><div class='metric-label'>Total FMV</div><div class='metric-value'>Rs.{ltv_summary['total_fmv']:,.0f}</div></div>", unsafe_allow_html=True)
    with k7: st.markdown(f"<div class='metric-card'><div class='metric-label'>Weighted LTV</div><div class='metric-value'>{ltv_summary['wtd_ltv']:.2f}%</div></div>", unsafe_allow_html=True)
    with k8: st.markdown(f"<div class='metric-card'><div class='metric-label'>Aggregate LTV</div><div class='metric-value'>{ltv_summary['aggregate_ltv']:.2f}%</div></div>", unsafe_allow_html=True)
    
    if ltv_overall_pass:
        st.markdown("<div class='status-banner status-banner-pass'>✅ LTV PORTFOLIO APPROVED</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='status-banner status-banner-fail'>️ LTV PORTFOLIO DECLINED</div>", unsafe_allow_html=True)
        
    disp_ltv = []
    for r in ltv_results:
        is_unsec = r.get('Is_Unsecured', False)
        ltv_val = r.get('LTV%')
        max_ltv = r.get('Max LTV%')
        
        if is_unsec: ltv_disp = "EXEMPT"
        elif r.get('No_FMV_Error'): ltv_disp = "NO FMV"
        elif ltv_val is None: ltv_disp = "N/A"
        else: ltv_disp = f"{ltv_val:.2f}%"
            
        disp_ltv.append({
            "ID": r.get('loan_account_id'), "Facility": r['Loan Type'], "Principal": f"Rs. {r['Principal']:,.0f}",
            "Total FMV": "N/A" if is_unsec else f"Rs. {r['Total FMV']:,.0f}",
            "LTV%": ltv_disp, "Max LTV%": "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%",
            "Status": "✅ PASS" if r['Pass_Status'] else " FAIL"
        })
    st.dataframe(pd.DataFrame(disp_ltv), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📄 Generate Continuous Report")
    ec1, ec2, ec3 = st.columns([2, 1, 1])
    with ec1:
        report_name = st.text_input("Client / Portfolio Name", placeholder="e.g. John Doe - Q1 Review", label_visibility="collapsed")
    with ec2:
        report_type = st.selectbox("Report Scope", ["Integrated (Both)", "DTI Only", "LTV Only"])
    with ec3:
        if st.button(" Generate PDF", type="primary", use_container_width=True):
            if not report_name.strip():
                st.error("Enter a client name.")
            else:
                with st.spinner("Generating continuous document..."):
                    r_type = 'Integrated' if 'Integrated' in report_type else ('DTI' if 'DTI' in report_type else 'LTV')
                    
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
                        'income_sources': st.session_state.income_sources if inc_mode == "Multiple Sources" else [],
                        'fmv_sources': st.session_state.fmv_sources
                    }
                        
                    try:
                        pdf_bytes = generate_integrated_pdf(report_name.strip(), payload)
                        st.session_state['generated_pdf'] = pdf_bytes
                        st.session_state['generated_pdf_name'] = f"{r_type}_Report_{report_name.strip().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        st.rerun()
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
                        
    if 'generated_pdf' in st.session_state:
        st.success("✅ Continuous Report generated successfully.")
        st.download_button(
            label="⬇️ Download PDF Now",
            data=st.session_state['generated_pdf'],
            file_name=st.session_state['generated_pdf_name'],
            mime="application/pdf",
            type="secondary",
            use_container_width=True
        )
else:
    st.info("👋 Add facilities using the form above to begin analysis. Ensure Income and Collateral configurations are set in the sidebar dropdowns.")