"""
NeoStats Glass Theme - Advanced CSS injection for Streamlit
"""

GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stApp"] {
    background: transparent !important;
    font-family: 'DM Sans', sans-serif;
    color: #e8eaf0 !important;
}

[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: -2;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.25) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 80% 90%, rgba(16,185,129,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 70% 50% at 60% 30%, rgba(139,92,246,0.12) 0%, transparent 50%),
        linear-gradient(135deg, #050810 0%, #0a0f1e 40%, #060c18 100%);
    animation: bgPulse 12s ease-in-out infinite alternate;
}

@keyframes bgPulse {
    0%   { filter: hue-rotate(0deg) brightness(1); }
    100% { filter: hue-rotate(15deg) brightness(1.05); }
}

[data-testid="stApp"]::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: -1;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 128px;
    pointer-events: none;
}

[data-testid="stSidebar"] {
    background: rgba(10, 15, 40, 0.7) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.4) !important;
}
[data-testid="stSidebar"] > div { background: transparent !important; }

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.5rem !important;
    backdrop-filter: blur(12px) !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px rgba(99,102,241,0.2) !important;
    border-color: rgba(99,102,241,0.4) !important;
}
[data-testid="metric-container"] label {
    color: rgba(200,205,230,0.7) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #a5b4fc !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
}

h1, h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; letter-spacing: -0.02em !important; }
h1 {
    background: linear-gradient(135deg, #a5b4fc 0%, #6ee7b7 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
h2 { color: #c7d2fe !important; }
h3 { color: #a5b4fc !important; font-size: 1rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }

[data-testid="stButton"] > button {
    background: linear-gradient(135deg, rgba(99,102,241,0.8) 0%, rgba(139,92,246,0.8) 100%) !important;
    border: 1px solid rgba(165,180,252,0.3) !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, rgba(99,102,241,1) 0%, rgba(139,92,246,1) 100%) !important;
    box-shadow: 0 0 24px rgba(99,102,241,0.5) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(165,180,252,0.2) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    outline: none !important;
}

[data-baseweb="select"] > div {
    background: rgba(10,15,40,0.9) !important;
    border: 1px solid rgba(165,180,252,0.2) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
}
[data-baseweb="popover"] {
    background: rgba(10,15,40,0.95) !important;
    border: 1px solid rgba(165,180,252,0.2) !important;
    backdrop-filter: blur(20px) !important;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

[data-testid="stAlert"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(165,180,252,0.2) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(12px) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: rgba(200,205,230,0.6) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(99,102,241,0.3) !important;
    color: #a5b4fc !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    margin-bottom: 4px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    color: rgba(200,205,230,0.8) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: #c7d2fe !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.7); }

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.4), transparent) !important;
    margin: 1.5rem 0 !important;
}

.page-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 0.72rem;
    font-family: 'DM Sans', sans-serif;
    color: #a5b4fc;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    margin-bottom: 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.3);
}

.risk-low {
    display: inline-block;
    background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.4);
    color: #6ee7b7;
    border-radius: 100px;
    padding: 4px 16px;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
}
.risk-medium {
    display: inline-block;
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    color: #fcd34d;
    border-radius: 100px;
    padding: 4px 16px;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
}
.risk-high {
    display: inline-block;
    background: rgba(239,68,68,0.15);
    border: 1px solid rgba(239,68,68,0.4);
    color: #fca5a5;
    border-radius: 100px;
    padding: 4px 16px;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
}

.chat-user {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px 16px 4px 16px;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0;
    font-family: 'DM Sans', sans-serif;
    color: #c7d2fe;
    max-width: 80%;
    margin-left: auto;
}
.chat-bot {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px 16px 16px 4px;
    padding: 0.8rem 1.2rem;
    margin: 0.5rem 0;
    font-family: 'DM Sans', sans-serif;
    color: #e8eaf0;
    max-width: 85%;
}
.sql-block {
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.5rem 0;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    color: #6ee7b7;
    overflow-x: auto;
}

.sidebar-brand {
    text-align: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 1.5rem;
}
.sidebar-brand h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #a5b4fc, #6ee7b7) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 !important;
}
.sidebar-brand .subtitle {
    font-size: 0.65rem;
    color: rgba(200,205,230,0.4);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-top: 2px;
}
.sidebar-brand .icon { font-size: 2.2rem; margin-bottom: 0.4rem; display: block; }

.sidebar-footer {
    position: absolute;
    bottom: 1.5rem;
    left: 0; right: 0;
    padding: 1rem 1.2rem 0;
    font-size: 0.68rem;
    color: rgba(200,205,230,0.3);
    border-top: 1px solid rgba(255,255,255,0.05);
}
.sidebar-footer .stack-item { display: flex; justify-content: space-between; padding: 2px 0; }
.sidebar-footer .stack-val { color: rgba(165,180,252,0.6); }

.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s ease-in-out infinite;
}
.status-dot.green { background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.5); }
.status-dot.red   { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.5); }
.status-dot.yellow{ background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.5); }
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
}

[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    border-radius: 100px !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stMarkdown"] p { color: rgba(200,205,230,0.85) !important; line-height: 1.7 !important; }
[data-testid="stMarkdown"] strong { color: #a5b4fc !important; }
</style>
"""


def inject_glass_theme():
    import streamlit as st
    st.markdown(GLASS_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str, badge: str = None):
    import streamlit as st
    badge_html = f'<div class="page-badge">⬡ {badge}</div>' if badge else ''
    st.markdown(f"""
    {badge_html}
    <h1 style="margin-top:0.2rem">{icon} {title}</h1>
    <p style="color:rgba(200,205,230,0.6);font-family:'DM Sans',sans-serif;margin-top:-0.5rem;margin-bottom:1.5rem;">{subtitle}</p>
    <hr>
    """, unsafe_allow_html=True)


def glass_metric(label: str, value: str, delta: str = None, icon: str = ""):
    delta_html = ""
    if delta:
        color = "#6ee7b7" if "+" in delta or delta.startswith("↑") else "#fca5a5"
        delta_html = f'<div style="font-size:0.78rem;color:{color};margin-top:4px">{delta}</div>'
    return f"""
    <div class="glass-card" style="padding:1.2rem 1.5rem;">
        <div style="font-size:0.7rem;color:rgba(200,205,230,0.5);text-transform:uppercase;letter-spacing:0.12em;font-family:'DM Sans',sans-serif">{icon} {label}</div>
        <div style="font-size:2rem;font-weight:800;font-family:'Syne',sans-serif;color:#a5b4fc;margin-top:4px">{value}</div>
        {delta_html}
    </div>
    """


def risk_badge(band: str) -> str:
    cls = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(band, "risk-medium")
    icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(band, "🟡")
    return f'<span class="{cls}">{icon} {band} Risk</span>'


def sidebar_brand():
    import streamlit as st
    st.markdown("""
    <div class="sidebar-brand">
        <span class="icon">🏛️</span>
        <h1>NeoStats</h1>
        <div class="subtitle">Credit Risk Platform</div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_footer(model="LightGBM + SHAP", llm="Groq · Llama-3", db="DuckDB", data="Home Credit"):
    import streamlit as st
    st.markdown(f"""
    <div class="sidebar-footer">
        <div class="stack-item"><span>Model</span><span class="stack-val">{model}</span></div>
        <div class="stack-item"><span>LLM</span><span class="stack-val">{llm}</span></div>
        <div class="stack-item"><span>DB</span><span class="stack-val">{db}</span></div>
        <div class="stack-item"><span>Data</span><span class="stack-val">{data}</span></div>
    </div>
    """, unsafe_allow_html=True)