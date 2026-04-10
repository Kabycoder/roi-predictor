"""styles.py — All CSS injected cleanly via st.markdown with unsafe_allow_html."""

FONTS = """
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
"""

CSS = """
<style>
:root {
  --bg:       #07090f;
  --bg2:      #0e1420;
  --bg3:      #141d2e;
  --border:   #1c2a3e;
  --border2:  #253548;
  --cyan:     #00e5ff;
  --purple:   #9b59ff;
  --green:    #00ffb3;
  --gold:     #ffcc00;
  --red:      #ff4757;
  --orange:   #ff7f50;
  --text:     #f0f4ff;
  --text2:    #7a90b0;
  --text3:    #3a4e65;
  --radius:   12px;
  --font-head: 'Times New Roman', 'Playfair Display', Georgia, serif;
  --font-mono: 'DM Mono', 'Courier New', monospace;
  --font-body: 'Times New Roman', Georgia, serif;
}

/* ── BASE ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 90% 60% at 15% 0%,   rgba(0,229,255,0.06)  0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 85% 100%,  rgba(155,89,255,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 50% 50%,   rgba(0,255,179,0.02)  0%, transparent 70%),
    var(--bg) !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarNav"] { display: none !important; }
/* header is NOT hidden here — hiding it removes the sidebar toggle button */
header[data-testid="stHeader"] { background: transparent !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0a0f1a 0%, #0d1525 100%) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── HEADINGS ── */
h1, h2, h3, h4 { font-family: var(--font-head) !important; }

/* ── PAGE HERO ── */
.hero {
  padding: 2rem 0 1.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.hero-eye {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--cyan);
  margin-bottom: 0.4rem;
}
.hero-title {
  font-family: var(--font-head);
  font-size: 2.6rem;
  font-weight: 900;
  color: var(--text);
  line-height: 1.05;
  margin: 0 0 0.5rem;
  letter-spacing: -0.01em;
}
.hero-title span {
  background: linear-gradient(90deg, var(--cyan), var(--purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 0.9rem;
  color: var(--text2);
  margin: 0;
  font-style: italic;
}

/* ── KPI CARDS ── */
.kpi {
  background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.3rem 1.5rem;
  position: relative;
  overflow: hidden;
  transition: all 0.25s ease;
}
.kpi::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: var(--radius) var(--radius) 0 0;
  opacity: 0.9;
}
.kpi.cyan::after  { background: linear-gradient(90deg, var(--cyan),   #0099ff); }
.kpi.purple::after{ background: linear-gradient(90deg, var(--purple), #ff59d6); }
.kpi.green::after { background: linear-gradient(90deg, var(--green),  #00cc88); }
.kpi.gold::after  { background: linear-gradient(90deg, var(--gold),   #ff9900); }
.kpi:hover { border-color: var(--border2); transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,0.4); }
.kpi-icon  { font-size: 1.6rem; margin-bottom: 0.5rem; }
.kpi-lbl   { font-family: var(--font-mono); font-size: 0.63rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text3); margin-bottom: 0.4rem; }
.kpi-val   { font-family: var(--font-head); font-size: 2.1rem; font-weight: 700; color: var(--text); line-height: 1; margin-bottom: 0.25rem; }
.kpi-dlt   { font-family: var(--font-mono); font-size: 0.72rem; color: var(--green); }

/* ── SECTION HEADER ── */
.sh {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.8rem 0 0.9rem;
}
.sh-bar {
  width: 4px; height: 1.2rem;
  background: linear-gradient(180deg, var(--cyan), var(--purple));
  border-radius: 3px; flex-shrink: 0;
}
.sh-title {
  font-family: var(--font-head);
  font-size: 1.1rem; font-weight: 700;
  color: var(--text); margin: 0;
}
.sh-tag {
  font-family: var(--font-mono);
  font-size: 0.62rem; letter-spacing: 0.1em;
  padding: 2px 9px; border-radius: 20px;
  background: rgba(0,229,255,0.08);
  border: 1px solid rgba(0,229,255,0.2);
  color: var(--cyan); text-transform: uppercase;
}

/* ── BUTTONS ── */
.stButton > button {
  background: linear-gradient(135deg, var(--cyan) 0%, var(--purple) 100%) !important;
  color: #fff !important;
  font-family: var(--font-head) !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  letter-spacing: 0.04em !important;
  border: none !important;
  border-radius: var(--radius) !important;
  padding: 0.7rem 2rem !important;
  transition: all 0.2s !important;
  box-shadow: 0 4px 20px rgba(0,229,255,0.25) !important;
}
.stButton > button:hover {
  opacity: 0.88 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 32px rgba(155,89,255,0.4) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text2) !important;
  font-family: var(--font-head) !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  padding: 0.6rem 1.3rem !important;
  border-bottom: 2px solid transparent !important;
  transition: color 0.2s !important;
  font-style: italic !important;
}
.stTabs [aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom-color: var(--cyan) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding-top: 1.2rem !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] {
  font-family: var(--font-mono) !important;
  font-size: 0.65rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--text3) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-head) !important;
  font-size: 1.65rem !important;
  font-weight: 700 !important;
  color: var(--text) !important;
}

/* ── FORM INPUTS ── */
div[data-baseweb="select"] > div {
  background: var(--bg3) !important;
  border-color: var(--border2) !important;
  color: var(--text) !important;
  border-radius: var(--radius) !important;
  font-family: var(--font-body) !important;
}
.stNumberInput input,
[data-testid="stTextInput"] input {
  background: var(--bg3) !important;
  border-color: var(--border2) !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
  border-radius: var(--radius) !important;
}
.stSlider [data-baseweb="slider"] { background: var(--border2) !important; }

/* ── ALERTS ── */
[data-testid="stInfo"] {
  background: rgba(0,229,255,0.05) !important;
  border: 1px solid rgba(0,229,255,0.2) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
}
[data-testid="stSuccess"] {
  background: rgba(0,255,179,0.05) !important;
  border: 1px solid rgba(0,255,179,0.2) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stWarning"] {
  background: rgba(255,204,0,0.05) !important;
  border: 1px solid rgba(255,204,0,0.2) !important;
  border-radius: var(--radius) !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  overflow: hidden !important;
}

/* ── PROGRESS ── */
[data-testid="stProgressBar"] > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--purple)) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  background: var(--bg3) !important;
  border: 1px dashed var(--border2) !important;
  border-radius: var(--radius) !important;
}

/* ── PREDICTION CARD ── */
.pred-wrap {
  background: linear-gradient(135deg, rgba(0,229,255,0.07) 0%, rgba(155,89,255,0.07) 100%);
  border: 1px solid rgba(0,229,255,0.3);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
}
.pred-num {
  font-family: var(--font-head);
  font-size: 5rem; font-weight: 900;
  background: linear-gradient(135deg, var(--cyan) 0%, var(--purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1; margin: 0.3rem 0;
}
.pred-lbl { font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text3); }
.pred-delta { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text2); margin: 0.4rem 0; }
.badge {
  display: inline-block; padding: 4px 16px; border-radius: 20px;
  font-family: var(--font-mono); font-size: 0.7rem; letter-spacing: 0.1em;
  text-transform: uppercase; margin-top: 0.7rem; font-weight: 500;
}
.badge-hi  { background: rgba(0,255,179,0.12); border: 1px solid rgba(0,255,179,0.35); color: var(--green); }
.badge-mid { background: rgba(255,204,0,0.12); border: 1px solid rgba(255,204,0,0.35);  color: var(--gold); }
.badge-lo  { background: rgba(255,71,87,0.12); border: 1px solid rgba(255,71,87,0.35);  color: var(--red); }

/* ── STEP CARDS ── */
.step {
  display: flex; gap: 1.2rem; align-items: flex-start;
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.1rem 1.4rem; margin-bottom: 0.75rem;
  transition: border-color 0.2s;
}
.step:hover { border-color: var(--border2); }
.step-num {
  font-family: var(--font-head); font-size: 1.6rem; font-weight: 900;
  color: var(--border2); flex-shrink: 0; line-height: 1;
  min-width: 2rem;
}
.step-title { font-family: var(--font-head); font-weight: 700; font-size: 0.95rem; color: var(--text); margin-bottom: 0.2rem; }
.step-desc  { font-size: 0.82rem; color: var(--text2); margin-bottom: 0.2rem; }
.step-code  { font-family: var(--font-mono); font-size: 0.7rem; color: var(--cyan); opacity: 0.85; }

/* ── ARCH TABLE ── */
.arch { width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 0.78rem; }
.arch th { color: var(--text3); font-size: 0.63rem; letter-spacing: 0.12em; text-transform: uppercase;
           padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--border); text-align: left; }
.arch td { padding: 0.65rem 0.8rem; border-bottom: 1px solid var(--border); color: var(--text2); }
.arch tr:last-child td { color: var(--cyan); border-bottom: none; background: rgba(0,229,255,0.03); }
.arch tr:hover td { background: var(--bg3); }
.atag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.68rem; }
.atag-relu   { background: rgba(155,89,255,0.15); border: 1px solid rgba(155,89,255,0.3); color: var(--purple); }
.atag-lin    { background: rgba(0,255,179,0.1);   border: 1px solid rgba(0,255,179,0.25); color: var(--green); }
.atag-none   { background: var(--bg3); border: 1px solid var(--border); color: var(--text3); }

/* ── FEAT CARD ── */
.feat {
  background: var(--bg2); border: 1px solid var(--border); border-radius: 10px;
  padding: 0.9rem 1.3rem; margin-bottom: 0.55rem;
  display: flex; justify-content: space-between; align-items: center;
  transition: border-color 0.2s;
}
.feat:hover { border-color: rgba(0,229,255,0.25); }
.feat-name { font-family: var(--font-mono); font-size: 0.82rem; color: var(--cyan); }
.feat-eq   { font-family: var(--font-mono); font-size: 0.75rem; color: var(--text3); margin-left: 1rem; }
.feat-why  { font-size: 0.78rem; color: var(--text2); font-style: italic; max-width: 38%; }

/* ── EMPTY STATE ── */
.empty {
  text-align: center; padding: 4rem 2rem;
  background: var(--bg2); border: 1px dashed var(--border2);
  border-radius: 16px; margin: 1rem 0;
}
.empty-icon { font-size: 3rem; opacity: 0.12; margin-bottom: 0.8rem; }
.empty-text { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text3); line-height: 1.8; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar       { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan); }

/* ── CODE INLINE ── */
code {
  font-family: var(--font-mono) !important;
  background: var(--bg3) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important; padding: 1px 6px !important;
  font-size: 0.82em !important; color: var(--cyan) !important;
}
</style>
"""

def inject(extra_html: str = ""):
    import streamlit as st
    st.markdown(FONTS + CSS + extra_html, unsafe_allow_html=True)
