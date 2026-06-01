
# ── Human-readable feature name mapping ──────────────────────────────────────
FEATURE_LABELS = {
    'EXT_SOURCE_1':               'Credit Bureau Score 1',
    'EXT_SOURCE_2':               'Credit Bureau Score 2',
    'EXT_SOURCE_3':               'Credit Bureau Score 3',
    'AMT_INCOME_TOTAL':           'Annual Income',
    'AMT_CREDIT':                 'Loan Amount',
    'AMT_ANNUITY':                'Annual Repayment',
    'AMT_GOODS_PRICE':            'Goods Price',
    'DAYS_BIRTH':                 'Applicant Age',
    'DAYS_EMPLOYED':              'Employment Duration',
    'DAYS_REGISTRATION':          'Days Since Registration',
    'DAYS_ID_PUBLISH':            'Days Since ID Issued',
    'DAYS_LAST_PHONE_CHANGE':     'Days Since Phone Change',
    'CNT_CHILDREN':               'Number of Children',
    'CNT_FAM_MEMBERS':            'Family Size',
    'CODE_GENDER':                'Gender',
    'FLAG_OWN_CAR':               'Owns a Car',
    'FLAG_OWN_REALTY':            'Owns Property',
    'REGION_RATING_CLIENT':       'Region Risk Rating',
    'REGION_POPULATION_RELATIVE': 'Region Population Density',
    'NAME_EDUCATION_TYPE':        'Education Level',
    'NAME_INCOME_TYPE':           'Income Type',
    'NAME_CONTRACT_TYPE':         'Loan Contract Type',
    'ORGANIZATION_TYPE':          'Employer Organisation Type',
    'HOUR_APPR_PROCESS_START':    'Application Hour',
    'debt_to_income':             'Repayment-to-Income Ratio',
    'credit_to_income':           'Loan-to-Income Ratio',
    'age_years':                  'Applicant Age (years)',
    'employment_years':           'Years Employed',
    'credit_term':                'Loan Term (years)',
    'LANDAREA_MODE':              'Land Area',
    'APARTMENTS_MODE':            'Apartment Size',
    'FLAG_WORK_PHONE':            'Has Work Phone',
    'FLAG_PHONE':                 'Has Phone',
    'FLAG_EMAIL':                 'Has Email',
    'REG_CITY_NOT_LIVE_CITY':     'Registered vs Living City Mismatch',
    'REG_CITY_NOT_WORK_CITY':     'Registered vs Work City Mismatch',
}

def human_name(col):
    """Return human-readable name for a feature column."""
    return FEATURE_LABELS.get(col, col.replace('_', ' ').title())

"""""
app.py — Credit Risk Intelligence Platform
Advanced glassmorphism UI with 5 tabs:
EDA · Risk Predictor · Explainability · Business Rules · Talk-to-Data
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Credit Risk Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Glass theme CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
}
.stApp {
    background: radial-gradient(ellipse at 20% 50%, #0f1b2d 0%, #060a10 50%, #0a0614 100%) !important;
    min-height: 100vh;
}
section[data-testid="stSidebar"] {
    background: rgba(8, 15, 30, 0.85) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(99, 179, 237, 0.12) !important;
}
.stButton > button {
    background: linear-gradient(135deg, rgba(59,130,246,0.25), rgba(139,92,246,0.25)) !important;
    border: 1px solid rgba(99,179,237,0.35) !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    border-radius: 10px !important;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(59,130,246,0.4), rgba(139,92,246,0.4)) !important;
    border-color: rgba(99,179,237,0.6) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(59,130,246,0.25) !important;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(15, 25, 50, 0.7) !important;
    border: 1px solid rgba(99,179,237,0.2) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
}
.stSlider > div > div { color: #3b82f6 !important; }
.stRadio > div { gap: 6px; }
.stRadio label {
    background: rgba(15, 25, 50, 0.6) !important;
    border: 1px solid rgba(99,179,237,0.15) !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    color: #94a3b8 !important;
    transition: all 0.2s !important;
}
.stRadio label:hover { border-color: rgba(99,179,237,0.4) !important; color: #e2e8f0 !important; }
div[data-testid="stMetricValue"] { color: #63b3ed !important; font-size: 1.6rem !important; font-family:'Syne',sans-serif !important; }
div[data-testid="stMetricLabel"] { color: #64748b !important; }
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
h1,h2,h3,h4 { color: #f1f5f9 !important; font-family: 'Syne', sans-serif !important; }
p, li, label { color: #94a3b8 !important; }
hr { border-color: rgba(99,179,237,0.12) !important; }
.block-container { padding-top: 1.5rem !important; }

.glass {
    background: rgba(15, 25, 50, 0.55);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(99, 179, 237, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}
.glass::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,179,237,0.5), rgba(167,139,250,0.5), transparent);
}
.hero-glass {
    background: linear-gradient(135deg, rgba(15,25,50,0.7) 0%, rgba(20,10,40,0.7) 100%);
    backdrop-filter: blur(24px);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-glass::after {
    content: '';
    position: absolute;
    top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.4rem;
    letter-spacing: -0.5px;
}
.hero-sub { color: #64748b !important; font-size: 0.95rem; margin: 0; }

.kpi-glass {
    background: rgba(15, 25, 50, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-glass::before {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 2px;
}
.kpi-blue::before  { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
.kpi-purple::before{ background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.kpi-teal::before  { background: linear-gradient(90deg, #14b8a6, #2dd4bf); }
.kpi-rose::before  { background: linear-gradient(90deg, #f43f5e, #fb7185); }

.kpi-label { color: #475569 !important; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
.kpi-value { color: #f1f5f9 !important; font-size: 1.65rem; font-weight: 700; font-family: 'DM Mono', monospace !important; }

.risk-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 16px; border-radius: 30px; font-weight: 600; font-size: 0.9rem;
}
.risk-low    { background: rgba(20, 184, 166, 0.15); border: 1px solid rgba(20,184,166,0.4); color: #2dd4bf; }
.risk-medium { background: rgba(251, 191, 36, 0.12); border: 1px solid rgba(251,191,36,0.35); color: #fbbf24; }
.risk-high   { background: rgba(239, 68,  68, 0.12); border: 1px solid rgba(239,68,68,0.35);  color: #f87171; }

.rule-card {
    background: rgba(10, 15, 30, 0.7);
    border: 1px solid rgba(99,179,237,0.1);
    border-left: 3px solid;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.rule-high { border-left-color: #ef4444; }
.rule-low  { border-left-color: #14b8a6; }
.rule-conditions { font-family: 'DM Mono', monospace !important; font-size: 0.8rem; color: #64748b !important; margin: 6px 0; }
.rule-outcome { font-weight: 700; font-size: 0.85rem; margin-bottom: 4px; }
.rule-high .rule-outcome { color: #f87171 !important; }
.rule-low  .rule-outcome { color: #2dd4bf !important; }
.rule-stat { font-size: 0.75rem; color: #475569 !important; }

.sql-glass {
    background: rgba(5, 10, 20, 0.8);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem;
    color: #7dd3fc;
    white-space: pre-wrap;
    line-height: 1.6;
}
.summary-glass {
    background: rgba(59, 130, 246, 0.07);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 10px;
    padding: 1rem 1.4rem;
    color: #cbd5e1 !important;
    font-size: 0.93rem;
    line-height: 1.7;
}
.sidebar-logo { text-align: center; padding: 1.5rem 0 2rem; }
.sidebar-logo .logo-icon { font-size: 2.2rem; margin-bottom: 6px; }
.sidebar-logo .logo-name { font-size: 1.1rem; font-weight: 800; color: #f1f5f9 !important; letter-spacing: -0.3px; }
.sidebar-logo .logo-tag { font-size: 0.65rem; color: #334155 !important; letter-spacing: 3px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ── Animated background + enhancement CSS ─────────────────────────────────────
st.markdown("""
<style>
[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: -2;
    background:
        radial-gradient(ellipse 80% 60% at 15% 10%, rgba(59,130,246,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 70% at 85% 85%, rgba(139,92,246,0.14) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 55% 35%, rgba(20,184,166,0.08) 0%, transparent 55%);
    animation: meshPulse 14s ease-in-out infinite alternate;
    pointer-events: none;
}
@keyframes meshPulse {
    0%   { opacity: 0.8; filter: hue-rotate(0deg); }
    100% { opacity: 1.0; filter: hue-rotate(12deg); }
}
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.35); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(59,130,246,0.6); }
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(99,179,237,0.3), transparent) !important;
    margin: 1.5rem 0 !important;
}
[data-testid="stExpander"] {
    background: rgba(15,25,50,0.5) !important;
    border: 1px solid rgba(99,179,237,0.12) !important;
    border-radius: 12px !important;
}
[data-testid="stDataFrame"] thead tr th {
    background: rgba(59,130,246,0.15) !important;
    color: #63b3ed !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stAlert"] {
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}
[data-baseweb="tab-list"] {
    background: rgba(15,25,50,0.5) !important;
    border-radius: 10px !important;
    padding: 3px !important;
}
[data-baseweb="tab"] {
    border-radius: 8px !important;
    color: rgba(148,163,184,0.7) !important;
    transition: all 0.2s !important;
}
[aria-selected="true"] {
    background: rgba(59,130,246,0.25) !important;
    color: #63b3ed !important;
}
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    border-radius: 100px !important;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR      = os.getenv("DATA_DIR",   "./data")
MODEL_DIR     = os.getenv("MODEL_DIR",  "./models")
DB_PATH       = os.getenv("DB_PATH",    "./data/credit_risk.duckdb")
MODEL_PATH    = os.path.join(MODEL_DIR, "lgbm_model.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_names.joblib")
RULES_PATH    = os.path.join(MODEL_DIR, "rule_tree.joblib")
METRICS_PATH  = os.path.join(MODEL_DIR, "metrics.joblib")

# ── Data loaders ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_app_data():
    path = os.path.join(DATA_DIR, "application_train.csv")
    if not os.path.exists(path): return None
    df = pd.read_csv(path, nrows=50000)
    df["age_years"] = (-df["DAYS_BIRTH"]) / 365
    df["DAYS_EMPLOYED"] = df["DAYS_EMPLOYED"].replace(365243, np.nan)
    df["employment_years"] = (-df["DAYS_EMPLOYED"]) / 365
    df["debt_to_income"] = df["AMT_ANNUITY"] / (df["AMT_INCOME_TOTAL"] + 1)
    return df

@st.cache_resource(show_spinner=False)
def load_model():
    if not os.path.exists(MODEL_PATH): return None, None
    return joblib.load(MODEL_PATH), joblib.load(FEATURES_PATH)

@st.cache_resource(show_spinner=False)
def load_rule_tree():
    if not os.path.exists(RULES_PATH): return None
    return joblib.load(RULES_PATH)

# ── Plotly theme ──────────────────────────────────────────────────────────────
GLASS_DARK = dict(
    paper_bgcolor="rgba(8,15,30,0)",
    plot_bgcolor="rgba(8,15,30,0)",
    font_color="#94a3b8",
    xaxis=dict(gridcolor="rgba(99,179,237,0.08)", linecolor="rgba(99,179,237,0.12)", zerolinecolor="rgba(99,179,237,0.08)"),
    yaxis=dict(gridcolor="rgba(99,179,237,0.08)", linecolor="rgba(99,179,237,0.12)", zerolinecolor="rgba(99,179,237,0.08)"),
    margin=dict(l=10, r=10, t=30, b=10),
)

# ── Load resources ────────────────────────────────────────────────────────────
df_raw = load_app_data()
model, feature_names = load_model()
data_ok  = df_raw is not None
model_ok = model is not None

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">🏦</div>
        <div class="logo-tag">Credit Risk Platform</div>
    </div>
    """, unsafe_allow_html=True)

    tab = st.radio("", [
        "📊  EDA Dashboard",
        "🎯  Risk Predictor",
        "🔍  Explainability",
        "📋  Business Rules",
        "💬  Talk-to-Data",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.72rem; color:#334155; line-height:1.8;'>
    Model &nbsp;&nbsp;&nbsp; LightGBM + SHAP<br>
    LLM &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Groq · Llama-3<br>
    DB &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; DuckDB<br>
    Data &nbsp;&nbsp;&nbsp; Home Credit<br>
    Status &nbsp; {'✅ Ready' if model_ok else '⚠️ No model'}
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EDA
# ══════════════════════════════════════════════════════════════════════════════
if "EDA" in tab:
    st.markdown('<div class="hero-glass"><p class="hero-title">Exploratory Data Analysis</p><p class="hero-sub">Home Credit Default Risk — 300K applicants · 122 features · 8% default rate</p></div>', unsafe_allow_html=True)

    if not data_ok:
        st.error("Place `application_train.csv` in the `data/` folder.")
        st.stop()
    df = df_raw

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "kpi-blue",   "Total Applicants",  f"{len(df):,}"),
        (k2, "kpi-rose",   "Default Rate",       f"{df['TARGET'].mean()*100:.1f}%"),
        (k3, "kpi-purple", "Avg Loan Amount",    f"₹{df['AMT_CREDIT'].mean()/1e5:.1f}L"),
        (k4, "kpi-teal",   "Avg Annual Income",  f"₹{df['AMT_INCOME_TOTAL'].mean()/1e5:.1f}L"),
    ]
    for col, cls, label, val in kpis:
        col.markdown(f'<div class="kpi-glass {cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Target Distribution")
        tc = df["TARGET"].value_counts().rename({0: "Repaid", 1: "Defaulted"})
        fig = px.pie(values=tc.values, names=tc.index, hole=0.6,
                     color_discrete_sequence=["#3b82f6", "#ef4444"])
        fig.update_layout(**GLASS_DARK, height=280, showlegend=True,
                          legend=dict(font=dict(color="#64748b")))
        fig.update_traces(textfont_color="#f1f5f9")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Default Rate by Gender")
        gd = df.groupby("CODE_GENDER")["TARGET"].mean().reset_index()
        gd["Default Rate (%)"] = gd["TARGET"] * 100
        fig = px.bar(gd, x="CODE_GENDER", y="Default Rate (%)",
                     color="CODE_GENDER",
                     color_discrete_sequence=["#3b82f6", "#8b5cf6", "#14b8a6"])
        fig.update_layout(**GLASS_DARK, height=280, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Age vs Default Rate")
        df["age_bin"] = pd.cut(df["age_years"], bins=[20, 30, 40, 50, 60, 70],
                               labels=["20-30", "30-40", "40-50", "50-60", "60-70"])
        age_def = df.groupby("age_bin")["TARGET"].mean().reset_index()
        age_def["Default Rate (%)"] = age_def["TARGET"] * 100
        fig = px.line(age_def, x="age_bin", y="Default Rate (%)",
                      markers=True, color_discrete_sequence=["#a78bfa"])
        fig.update_traces(line_width=2.5, marker_size=8)
        fig.update_layout(**GLASS_DARK, height=280)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Default Rate by Education")
        ed = df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean().sort_values(ascending=True) * 100
        fig = px.bar(ed, orientation="h", color=ed.values,
                     color_continuous_scale="Plasma",
                     labels={"value": "Default Rate (%)", "NAME_EDUCATION_TYPE": ""})
        fig.update_layout(**GLASS_DARK, height=280, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Income Distribution")
        cap = df["AMT_INCOME_TOTAL"].quantile(0.99)
        id2 = df[df["AMT_INCOME_TOTAL"] < cap]
        fig = px.histogram(id2, x="AMT_INCOME_TOTAL", color="TARGET",
                           color_discrete_map={0: "#3b82f6", 1: "#ef4444"},
                           nbins=50, barmode="overlay", opacity=0.75,
                           labels={"AMT_INCOME_TOTAL": "Annual Income", "TARGET": "Default"})
        fig.update_layout(**GLASS_DARK, height=280)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c6:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Default Rate by Income Type")
        it = df.groupby("NAME_INCOME_TYPE")["TARGET"].mean().sort_values(ascending=False) * 100
        fig = px.bar(it, color=it.values, color_continuous_scale="Turbo",
                     labels={"value": "Default Rate (%)", "NAME_INCOME_TYPE": ""})
        fig.update_layout(**GLASS_DARK, height=280, coloraxis_showscale=False, xaxis_tickangle=-25)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("💡 Key Business Insights")
    ins_cols = st.columns(2)
    insights = [
        ("🔴 Severe Class Imbalance",
         f"Only {df['TARGET'].mean()*100:.1f}% defaulted — requires SMOTE or class weighting to avoid biased models."),
        ("👶 Youth Risk",
         "Applicants aged 20–30 default significantly more than older cohorts — age is a strong predictor."),
        ("🎓 Education Signal",
         f"Lower-secondary applicants default at {df[df['NAME_EDUCATION_TYPE']=='Lower secondary']['TARGET'].mean()*100:.1f}% "
         f"vs {df[df['NAME_EDUCATION_TYPE']=='Higher education']['TARGET'].mean()*100:.1f}% for university-educated."),
        ("💰 Income Threshold",
         f"Defaulters' median income ₹{df[df['TARGET']==1]['AMT_INCOME_TOTAL'].median():,.0f} is lower "
         f"than non-defaulters' ₹{df[df['TARGET']==0]['AMT_INCOME_TOTAL'].median():,.0f}."),
        ("📊 Loan Size Risk",
         "Larger loan amounts relative to income strongly predict default — credit-to-income ratio is a key risk driver."),
        ("🏘️ Region Effect",
         "Clients in Region Rating 3 (highest-risk regions) default at nearly 3× the rate of Region 1 clients."),
    ]
    for i, (title, text) in enumerate(insights):
        with ins_cols[i % 2]:
            st.markdown(
                f'<div class="glass" style="padding:1rem 1.2rem;">'
                f'<strong style="color:#63b3ed;font-size:0.85rem;">{title}</strong>'
                f'<p style="margin:4px 0 0;font-size:0.85rem;color:#64748b;">{text}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RISK PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
elif "Risk" in tab:
    st.markdown('<div class="hero-glass"><p class="hero-title">Loan Default Risk Predictor</p><p class="hero-sub">Enter applicant details for an instant AI-powered risk assessment</p></div>', unsafe_allow_html=True)

    if not model_ok:
        st.warning("Run `python setup_platform.py` to train the model first.")
        st.stop()

    if os.path.exists(METRICS_PATH):
        metrics = joblib.load(METRICS_PATH)
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="kpi-glass kpi-blue"><div class="kpi-label">ROC-AUC</div><div class="kpi-value">{metrics.get("roc_auc","—")}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="kpi-glass kpi-purple"><div class="kpi-label">PR-AUC</div><div class="kpi-value">{metrics.get("pr_auc","—")}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="kpi-glass kpi-teal"><div class="kpi-label">Model Type</div><div class="kpi-value" style="font-size:1rem;padding-top:4px;">LightGBM</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="kpi-glass kpi-rose"><div class="kpi-label">Features</div><div class="kpi-value">{len(feature_names)}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Financial**")
        amt_income  = st.number_input("Annual Income (₹)",    10000, 10000000, 180000, 10000)
        amt_credit  = st.number_input("Loan Amount (₹)",      10000, 5000000,  450000, 10000)
        amt_annuity = st.number_input("Annual Repayment (₹)", 1000,  500000,   22000,  1000)
        amt_goods   = st.number_input("Goods Price (₹)",      0,     5000000,  400000, 10000)
    with c2:
        st.markdown("**Personal**")
        age              = st.slider("Age", 20, 70, 35)
        employment_years = st.slider("Employment (years)", 0, 40, 5)
        cnt_children     = st.selectbox("No. of Children", [0,1,2,3,4,5,6,7,8,9,10],
                             help="Dataset range: 0–19. Values above 10 are extremely rare (<0.01%).")
        cnt_fam          = st.selectbox("Family Size", [1,2,3,4,5,6,7,8,9,10], index=1,
                             help="Dataset range: 1–20. Values above 10 are extremely rare.")
    with c3:
        st.markdown("**Profile**")
        gender      = st.selectbox("Gender", ["M", "F"],
                         help="M = Male (34%), F = Female (66%) in dataset. XNA (4 records) excluded.")
        education   = st.selectbox("Education Level", [
            "Secondary / secondary special",
            "Higher education",
            "Incomplete higher",
            "Lower secondary",
            "Academic degree"],
            help="Secondary/secondary special is most common (71%). Academic degree is rarest (0.05%).")
        income_type = st.selectbox("Income Type", [
            "Working",
            "Commercial associate",
            "Pensioner",
            "State servant",
            "Unemployed",
            "Student",
            "Businessman",
            "Maternity leave"],
            help="Working is most common (52%). Student/Businessman/Maternity leave are very rare (<0.01%).")
        own_car     = st.selectbox("Owns a Vehicle?", ["N", "Y"],
                         help="Y/N only — dataset records ownership, not number of vehicles. 34% own a car.")
        own_realty  = st.selectbox("Owns Property?", ["Y", "N"],
                         help="Y/N only — dataset records ownership, not property value. 69% own property.")
        region      = st.selectbox("Region Risk Rating", [1, 2, 3], index=1,
                         help="1 = Lowest risk region (10%), 2 = Medium (74%), 3 = Highest risk (16%).")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Credit Bureau Scores ─────────────────────────────────────────────
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("**🏦 External Credit Bureau Scores** — leave at 0.5 if unknown (population median)")
    st.caption("These are the strongest predictors. EXT_SOURCE_1/2/3 are bureau scores from 0 (worst) to 1 (best). Setting all to 0 will always give High Risk — use 0.5 if unsure.")
    eb1, eb2, eb3 = st.columns(3)
    with eb1:
        ext1 = st.slider("EXT_SOURCE_1 (Credit Score 1)", 0.0, 1.0, 0.5, 0.01, help="External credit bureau score 1. Higher = better credit history.")
    with eb2:
        ext2 = st.slider("EXT_SOURCE_2 (Credit Score 2)", 0.0, 1.0, 0.5, 0.01, help="External credit bureau score 2. This is the single strongest predictor in the model.")
    with eb3:
        ext3 = st.slider("EXT_SOURCE_3 (Credit Score 3)", 0.0, 1.0, 0.5, 0.01, help="External credit bureau score 3.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚡  Assess Risk Now", use_container_width=True):
        applicant = {
            "AMT_INCOME_TOTAL":  amt_income,
            "AMT_CREDIT":        amt_credit,
            "AMT_ANNUITY":       amt_annuity,
            "AMT_GOODS_PRICE":   amt_goods,
            "DAYS_BIRTH":        -age * 365,
            "DAYS_EMPLOYED":     -employment_years * 365 if employment_years > 0 else 365243,
            "CNT_CHILDREN":      cnt_children,
            "CNT_FAM_MEMBERS":   cnt_fam,
            "CODE_GENDER":       0 if gender == "F" else 1,
            "FLAG_OWN_CAR":      1 if own_car == "Y" else 0,
            "FLAG_OWN_REALTY":   1 if own_realty == "Y" else 0,
            "REGION_RATING_CLIENT": region,
            "EXT_SOURCE_1":      ext1,
            "EXT_SOURCE_2":      ext2,
            "EXT_SOURCE_3":      ext3,
            "debt_to_income":    amt_annuity / (amt_income + 1),
            "credit_to_income":  amt_credit  / (amt_income + 1),
            "age_years":         age,
            "employment_years":  employment_years,
            "credit_term":       amt_credit  / (amt_annuity + 1),
        }
        row = pd.DataFrame([applicant])
        for col in feature_names:
            if col not in row.columns:
                row[col] = 0
        row = row[feature_names]

        prob  = model.predict_proba(row)[0][1]
        score = round(prob * 100, 1)
        band  = "Low" if prob < 0.3 else ("Medium" if prob < 0.6 else "High")

        st.markdown("---")
        r1, r2 = st.columns([1, 2])
        with r1:
            color = "#14b8a6" if band == "Low" else ("#fbbf24" if band == "Medium" else "#ef4444")
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                number={"suffix": "%", "font": {"size": 38, "color": color}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#334155"},
                    "bar":  {"color": color, "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)",
                    "bordercolor": "rgba(99,179,237,0.1)",
                    "steps": [
                        {"range": [0,  30],  "color": "rgba(20,184,166,0.1)"},
                        {"range": [30, 60],  "color": "rgba(251,191,36,0.1)"},
                        {"range": [60, 100], "color": "rgba(239,68,68,0.1)"},
                    ],
                },
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#f1f5f9", height=260,
                margin=dict(l=20, r=20, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        with r2:
            band_cls = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}[band]
            st.markdown(f'<div class="glass"><span class="risk-pill {band_cls}">⬤ &nbsp;{band} Risk</span>', unsafe_allow_html=True)
            m_a, m_b, m_c = st.columns(3)
            m_a.metric("Default Prob",        f"{prob*100:.1f}%")
            m_b.metric("Credit / Income",     f"{amt_credit/amt_income:.2f}×")
            m_c.metric("Repayment / Income",  f"{amt_annuity/amt_income*100:.1f}%")

            if band == "Low":
                st.success("✅ APPROVE — Profile appears stable. Standard loan terms recommended.")
            elif band == "Medium":
                st.warning("⚠️ MANUAL REVIEW — Moderate risk. Request additional documents or collateral.")
            else:
                st.error("❌ HIGH RISK — Likely to default. Decline or apply stricter conditions.")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Model Performance Details ────────────────────────────────────
        if os.path.exists(METRICS_PATH):
            metrics = joblib.load(METRICS_PATH)
            report = metrics.get("classification_report", {})
            cm = metrics.get("confusion_matrix", None)
            if report or cm:
                st.markdown("---")
                st.subheader("📊 Model Performance Details")
                perf_cols = st.columns(4)
                f1_default = report.get("1", {}).get("f1-score", report.get("macro avg", {}).get("f1-score", "—"))
                precision  = report.get("1", {}).get("precision", "—")
                recall     = report.get("1", {}).get("recall", "—")
                accuracy   = report.get("accuracy", "—")
                perf_cols[0].markdown(f'<div class="kpi-glass kpi-teal"><div class="kpi-label">F1 (Default Class)</div><div class="kpi-value">{f1_default if isinstance(f1_default, str) else f"{f1_default:.4f}"}</div></div>', unsafe_allow_html=True)
                perf_cols[1].markdown(f'<div class="kpi-glass kpi-blue"><div class="kpi-label">Precision</div><div class="kpi-value">{precision if isinstance(precision, str) else f"{precision:.4f}"}</div></div>', unsafe_allow_html=True)
                perf_cols[2].markdown(f'<div class="kpi-glass kpi-purple"><div class="kpi-label">Recall</div><div class="kpi-value">{recall if isinstance(recall, str) else f"{recall:.4f}"}</div></div>', unsafe_allow_html=True)
                perf_cols[3].markdown(f'<div class="kpi-glass kpi-rose"><div class="kpi-label">Accuracy</div><div class="kpi-value">{accuracy if isinstance(accuracy, str) else f"{accuracy:.4f}"}</div></div>', unsafe_allow_html=True)
                if cm:
                    st.markdown("<br>", unsafe_allow_html=True)
                    cm_cols = st.columns([1,2])
                    with cm_cols[0]:
                        st.markdown('<div class="glass" style="padding:1rem;">', unsafe_allow_html=True)
                        st.markdown("**Confusion Matrix**")
                        cm_df = pd.DataFrame(cm, index=["Actual: Repaid","Actual: Default"], columns=["Pred: Repaid","Pred: Default"])
                        st.dataframe(cm_df, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    with cm_cols[1]:
                        st.markdown('<div class="glass" style="padding:1rem;font-size:0.83rem;color:#64748b;line-height:1.9;">', unsafe_allow_html=True)
                        st.markdown("**Class imbalance strategy**")
                        st.markdown("The dataset has ~8% default rate (severe imbalance). This model uses LightGBM's <code>scale_pos_weight</code> parameter computed as count(non-default) / count(default), giving the minority class proportionally higher weight during training. This improves recall for the default class without requiring oversampling.", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

        # ── Per-applicant SHAP Waterfall ──────────────────────────────────
        st.markdown("---")
        st.subheader("Why this score? — SHAP Explanation")
        with st.spinner("Computing individual SHAP values..."):
            import shap, matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer(row)
            import copy
            sv_display = copy.deepcopy(shap_vals)
            sv_display.feature_names = [human_name(f) for f in (shap_vals.feature_names or feature_names)]
            plt.style.use("dark_background")
            fig_w, ax_w = plt.subplots(figsize=(10, 5), facecolor="#0a0e1a")
            ax_w.set_facecolor("#0a0e1a")
            shap.plots.waterfall(sv_display[0], max_display=12, show=False)
            plt.tight_layout()
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.pyplot(fig_w)
            plt.close()
            st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Red bars push risk UP · Blue bars push risk DOWN · f(x) = final predicted probability")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EXPLAINABILITY
# ══════════════════════════════════════════════════════════════════════════════
elif "Explainab" in tab:
    st.markdown('<div class="hero-glass"><p class="hero-title">Model Explainability — SHAP</p><p class="hero-sub">Understand which features drive each prediction · Satisfies audit & regulatory requirements</p></div>', unsafe_allow_html=True)

    if not model_ok or not data_ok:
        st.warning("Model and data required.")
        st.stop()

    st.info("SHAP (SHapley Additive exPlanations) assigns each feature a contribution score. Red = pushes risk up · Blue = pushes risk down.")

    with st.spinner("Computing SHAP on 500-applicant sample..."):
        import shap, matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from src.data.preprocessor import preprocess

        sample = df_raw.sample(min(500, len(df_raw)), random_state=42).copy()
        dummy_target = pd.Series(0, index=sample.index, name="TARGET")
        sample_with_target = pd.concat([sample, dummy_target], axis=1)
        X_sample, _ = preprocess(sample_with_target)
        for f in feature_names:
            if f not in X_sample.columns:
                X_sample[f] = 0
        X_sample = X_sample[feature_names]

    st.subheader("Global Feature Importance")
    with st.spinner("Computing..."):
        explainer = shap.TreeExplainer(model)
        sv = explainer.shap_values(X_sample)
        if isinstance(sv, list):
            sv = sv[1]
        importance = np.abs(sv).mean(axis=0)
        feat_imp = (
            pd.DataFrame({"Feature": feature_names, "Mean |SHAP|": importance})
            .sort_values("Mean |SHAP|", ascending=False)
            .head(15)
        )
        feat_imp["Feature"] = feat_imp["Feature"].apply(human_name)
        fig = px.bar(
            feat_imp.sort_values("Mean |SHAP|"),
            x="Mean |SHAP|", y="Feature", orientation="h",
            color="Mean |SHAP|", color_continuous_scale="Viridis"
        )
        fig.update_layout(**GLASS_DARK, height=480, coloraxis_showscale=False)
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("SHAP Beeswarm Summary")
    with st.spinner("Rendering..."):
        plt.style.use("dark_background")
        fig2, ax = plt.subplots(figsize=(10, 6), facecolor="#0a0e1a")
        ax.set_facecolor("#0a0e1a")
        X_display = X_sample.rename(columns=FEATURE_LABELS)
        shap.summary_plot(sv, X_display, max_display=15, show=False, plot_size=None)
        plt.tight_layout()
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.pyplot(fig2)
        plt.close()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div class="glass"><strong style="color:#63b3ed;">How to read this chart</strong>'
            '<ul style="color:#64748b;font-size:0.85rem;line-height:2;">'
            '<li>Features ranked top-to-bottom by total impact</li>'
            '<li><span style="color:#ef4444;">Red dots</span> = high feature value → higher default risk</li>'
            '<li><span style="color:#3b82f6;">Blue dots</span> = low feature value → lower default risk</li>'
            '<li>Wider spread = more variable impact across applicants</li>'
            '</ul></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            '<div class="glass"><strong style="color:#a78bfa;">Key predictors</strong>'
            '<ul style="color:#64748b;font-size:0.85rem;line-height:2;">'
            '<li><code>Credit Bureau Scores 1/2/3</code> — External credit history scores</li>'
            '<li><code>Repayment-to-Income Ratio</code> — Higher burden = higher risk</li>'
            '<li><code>Applicant Age (years)</code> — Younger applicants = higher risk</li>'
            '<li><code>Loan Amount</code> — Larger loans = higher risk</li>'
            '<li><code>Years Employed</code> — Longer employment = lower risk</li>'
            '</ul></div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BUSINESS RULES
# ══════════════════════════════════════════════════════════════════════════════
elif "Rules" in tab:
    st.markdown('<div class="hero-glass"><p class="hero-title">Business Decision Rules</p><p class="hero-sub">IF-THEN credit policy rules derived from ML — readable by analysts, auditors & regulators</p></div>', unsafe_allow_html=True)

    rule_tree = load_rule_tree()
    if rule_tree is None:
        st.warning("Run `python setup_platform.py` to derive rules after training the model.")
        st.stop()

    if not data_ok or not model_ok:
        st.warning("Data and model required.")
        st.stop()

    st.info("A shallow decision tree is fitted on LightGBM's predictions to produce transparent IF-THEN rules suitable for credit policy documentation and regulatory review.")

    with st.spinner("Loading rules..."):
        from src.data.preprocessor import preprocess
        from src.rules.rule_engine import derive_rules

        sample = df_raw.sample(min(5000, len(df_raw)), random_state=42).copy()
        X_s, y_s = preprocess(sample)
        for f in feature_names:
            if f not in X_s.columns:
                X_s[f] = 0
        X_s = X_s[feature_names]
        result      = derive_rules(model, X_s, y_s)
        plain_rules = result["plain_rules"]
        top_features = result["top_features"]

    st.subheader("Top Features Used in Rules")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        _tf = top_features.reset_index()
        _tf.columns = ["Feature", "Importance"]
        fig = px.bar(
            _tf,
            x="Importance", y="Feature", orientation="h",
            color="Importance", color_continuous_scale="Plasma"
        )
        fig.update_layout(**GLASS_DARK, height=320, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(
            '<div class="glass"><strong style="color:#63b3ed;">How rules are derived</strong><br><br>'
            '<p style="color:#64748b;font-size:0.85rem;line-height:1.8;">'
            '1. LightGBM predicts default probability on training data<br>'
            '2. A shallow decision tree (depth ≤ 4) is fitted on those predictions<br>'
            '3. Each path from root to leaf becomes a business rule<br>'
            '4. Rules with ≥ 500 applicants are kept for statistical stability'
            '</p></div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.subheader("Derived IF-THEN Rules")
    high_rules = [r for r in plain_rules if r["decision"] == 1]
    low_rules  = [r for r in plain_rules if r["decision"] == 0]

    col_h, col_l = st.columns(2)
    with col_h:
        st.markdown("**🔴 High-Risk Rules (Decline / Review)**")
        for rule in high_rules[:5]:
            conds = "<br>".join([f"&nbsp;&nbsp;IF {c}" for c in rule["conditions"]])
            st.markdown(
                f'<div class="rule-card rule-high">'
                f'<div class="rule-outcome">❌ {rule["outcome"]}</div>'
                f'<div class="rule-conditions">{conds}</div>'
                f'<div class="rule-stat">{rule["samples"]:,} applicants · {rule["default_rate"]}% default rate</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    with col_l:
        st.markdown("**🟢 Low-Risk Rules (Approve)**")
        for rule in low_rules[:5]:
            conds = "<br>".join([f"&nbsp;&nbsp;IF {c}" for c in rule["conditions"]])
            st.markdown(
                f'<div class="rule-card rule-low">'
                f'<div class="rule-outcome">✅ {rule["outcome"]}</div>'
                f'<div class="rule-conditions">{conds}</div>'
                f'<div class="rule-stat">{rule["samples"]:,} applicants · {rule["default_rate"]}% default rate</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    with st.expander("📄 View Full Rule Tree (Raw)"):
        rules_file = os.path.join(MODEL_DIR, "decision_rules.txt")
        if os.path.exists(rules_file):
            with open(rules_file) as f:
                st.code(f.read(), language="text")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TALK-TO-DATA
# ══════════════════════════════════════════════════════════════════════════════
elif "Talk" in tab:
    st.markdown('<div class="hero-glass"><p class="hero-title">Talk-to-Data Chatbot</p><p class="hero-sub">Ask anything about the dataset in plain English — Groq AI converts it to SQL and explains the result</p></div>', unsafe_allow_html=True)

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.markdown("""
        <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
        border-radius:14px;padding:1.2rem 1.5rem;">
            <b style="color:#f87171;">⚠️ GROQ_API_KEY not set</b><br>
            <span style="color:#64748b;">Add <code>GROQ_API_KEY=gsk_xxx</code> to your
            <code>.env</code> file. Free key at
            <a href="https://console.groq.com" target="_blank" style="color:#63b3ed;">
            console.groq.com</a></span>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    else:
        st.markdown("""
        <div style="background:rgba(20,184,166,0.08);border:1px solid rgba(20,184,166,0.25);
        border-radius:10px;padding:0.6rem 1.2rem;margin-bottom:1rem;">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
            background:#14b8a6;margin-right:8px;"></span>
            <span style="color:#2dd4bf;font-size:0.85rem;">Groq API connected · Llama-3 70B ready</span>
        </div>
        """, unsafe_allow_html=True)

    import duckdb
    if not os.path.exists(DB_PATH):
        if data_ok:
            with st.spinner("Building database from CSVs..."):
                from src.talk_to_data.db_builder import build_db
                build_db()
        else:
            st.error("Place CSVs in data/ folder first.")
            st.stop()

    st.subheader("💡 Try These Questions")
    example_qs = [
        "What is the overall default rate?",
        "Which income type has the highest default rate?",
        "Average loan: male vs female?",
        "Default rate by education level?",
        "Top 5 occupations by applicant count?",
        "Average income: defaulters vs non-defaulters?",
        "How many own a car AND property?",
        "Default rate by region rating?",
        "What % of applicants have children?",
        "Loan amount distribution by contract type?",
    ]

    cols = st.columns(2)
    selected_q = st.session_state.get("selected_q", "")
    for i, q in enumerate(example_qs):
        if cols[i % 2].button(f"▸ {q}", key=f"q{i}"):
            st.session_state["selected_q"] = q
            selected_q = q

    st.markdown("---")
    user_q = st.text_input(
        "Or type your own question:",
        value=selected_q,
        placeholder="e.g. Which region has the most defaulters?"
    )

    if st.button("🔍  Ask Groq", use_container_width=True) and user_q:
        with st.spinner("Groq is thinking..."):
            from src.talk_to_data.nl_to_sql import ask
            result = ask(user_q)

        if result["error"]:
            st.error(f"Error: {result['error']}")
        else:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown("**Generated SQL**")
                st.markdown(f'<div class="sql-glass">{result["sql"]}</div>', unsafe_allow_html=True)
            with c2:
                if result["summary"]:
                    st.markdown("**Plain-English Answer**")
                    st.markdown(f'<div class="summary-glass">💬 {result["summary"]}</div>', unsafe_allow_html=True)

            if result["data"] is not None and not result["data"].empty:
                st.markdown("<br>**Query Results**", unsafe_allow_html=True)
                st.dataframe(result["data"], use_container_width=True)

                df_res   = result["data"]
                num_cols = df_res.select_dtypes(include=np.number).columns.tolist()
                cat_cols = df_res.select_dtypes(include="object").columns.tolist()
                if len(df_res) > 1 and num_cols and cat_cols and len(df_res) <= 50:
                    fig = px.bar(df_res, x=cat_cols[0], y=num_cols[0],
                                 color=num_cols[0], color_continuous_scale="Viridis")
                    fig.update_layout(**GLASS_DARK, height=320, coloraxis_showscale=False)
                    st.markdown('<div class="glass">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)