"""
app.py — ROI Intelligence Platform
Vibrant dark theme · Times New Roman · CSS injected via styles.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from processor import DataProcessor
from model import ScratchNeuralNet
from styles import inject

# ── PAGE CONFIG ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Marketing Compaign Analysis",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject()   # ← all CSS lives in styles.py, injected once here

# ── PLOTLY THEME ───────────────────────────────────────────────────────
PL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, Courier New, monospace", color="#7a90b0", size=11),
    xaxis=dict(gridcolor="#1353ae", linecolor="#1c2a3e", zerolinecolor="#1c2a3e"),
    yaxis=dict(gridcolor="#1c2a3e", linecolor="#1c2a3e", zerolinecolor="#1c2a3e"),
    margin=dict(l=10, r=10, t=35, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    colorway=["#00e5ff","#9b59ff","#00ffb3","#ffcc00","#ff4757","#ff7f50"],
)

# ── SESSION STATE ──────────────────────────────────────────────────────
for k, v in {
    "df":None, "processor":None, "model":None,
    "X_train":None, "X_test":None, "y_train":None, "y_test":None,
    "trained":False, "loss_history":[], "val_loss_history":[],
    "y_pred_test":None, "page":"dashboard",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_df(b: bytes) -> pd.DataFrame:
    import io
    df = pd.read_csv(io.BytesIO(b))
    # Keep Acquisition_Cost as raw string — parse_cost() handles it later
    return df

def parse_cost(df):
    d = df.copy()

    # ✅ Normalize column names
    d.columns = d.columns.str.strip()
    d.columns = d.columns.str.replace(" ", "_")

    # ✅ Fix Channel
    if "Channel_Used" not in d.columns:
        for col in ["Channel", "channel", "Platform", "channel_used"]:
            if col in d.columns:
                d["Channel_Used"] = d[col]
                break
        else:
            d["Channel_Used"] = "Unknown"

    # ✅ Fix Campaign
    if "Campaign_Type" not in d.columns:
        for col in ["Campaign", "campaign", "campaign_type"]:
            if col in d.columns:
                d["Campaign_Type"] = d[col]
                break
        else:
            d["Campaign_Type"] = "General"

    # ✅ Detect cost column
    cost_col = next(
        (c for c in d.columns
         if c.lower().replace(" ", "_") in
         ["acquisition_cost", "budget", "cost", "spend", "ad_spend"]),
        None
    )

    if cost_col:
        if cost_col != "Acquisition_Cost":
            d = d.rename(columns={cost_col: "Acquisition_Cost"})

        if d["Acquisition_Cost"].dtype == object:
            d["Acquisition_Cost"] = (
                d["Acquisition_Cost"]
                .astype(str)
                .str.replace(r"[\$,]", "", regex=True)
                .astype(float)
            )
    else:
        d["Acquisition_Cost"] = 10000.0  # safe default, never zero

    # ✅ SAFE DEFAULT COLUMNS
    if "Engagement_Score" not in d.columns:
        d["Engagement_Score"] = 5.0
    if "Clicks" not in d.columns:
        d["Clicks"] = 500.0
    if "Impressions" not in d.columns:
        d["Impressions"] = 5000.0

    # ✅ NEVER overwrite ROI if it already exists in the dataset
    # Only compute ROI if dataset truly has no ROI column at all
    if "ROI" not in d.columns:
        if "Revenue" in d.columns and d["Acquisition_Cost"].sum() > 0:
            d["ROI"] = ((d["Revenue"] - d["Acquisition_Cost"]) /
                        (d["Acquisition_Cost"].replace(0, 1e-6))) * 100
        else:
            d["ROI"] = 5.0  # safe fallback average

    # ✅ Also fix Acquisition_Cost fallback — 0.0 caused -100% ROI
    if cost_col is None:
        d["Acquisition_Cost"] = 10000.0

    return d

def hero(eyebrow, title, highlight, sub):
    st.markdown(f"""
    <div class="hero">
      <div class="hero-eye">{eyebrow}</div>
      <h1 class="hero-title">{title} <span>{highlight}</span></h1>
      <p class="hero-sub">{sub}</p>
    </div>""", unsafe_allow_html=True)

def sh(title, tag=None):
    t = f'<span class="sh-tag">{tag}</span>' if tag else ""
    st.markdown(f"""
    <div class="sh">
      <div class="sh-bar"></div>
      <p class="sh-title">{title}</p>{t}
    </div>""", unsafe_allow_html=True)

def kpi(label, value, delta, icon, color):
    st.markdown(f"""
    <div class="kpi {color}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-dlt">{delta}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:1.5rem 0 1rem">
          <div style="font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.25em;
                      text-transform:uppercase;color:#3a4e65;margin-bottom:.4rem">Platform</div>
          <div style="font-family:'Times New Roman',Georgia,serif;font-size:1.5rem;
                      font-weight:900;color:#f0f4ff;line-height:1.15">
            ROI Intelligence
            <div style="font-family:'DM Mono',monospace;font-size:.8rem;font-weight:400;
                        background:linear-gradient(90deg,#00e5ff,#9b59ff);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text;margin-top:.1rem">◈ Neural Engine</div>
          </div>
        </div>
        <hr style="border-color:#1c2a3e;margin:.3rem 0 1rem">
        """, unsafe_allow_html=True)

        nav_items = [
            ("dashboard", "◈", "Executive Dashboard"),
            ("explorer",  "⬡", "Data Explorer"),
            ("predictor", "◎", "AI ROI Predictor"),
            ("lab",       "⬟", "Neural Lab"),
        ]
        for key, icon, label in nav_items:
            active = st.session_state.page == key
            style = ("background:rgba(0,229,255,0.08);border:1px solid rgba(0,229,255,0.2);"
                     "color:#00e5ff" if active else
                     "background:transparent;border:1px solid transparent;color:#7a90b0")
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()


        st.markdown("""
        <hr style="border-color:#1c2a3e;margin:1rem 0">
        <div style="font-family:'Times New Roman',Georgia,serif;font-size:.78rem;
                    color:#7a90b0;margin-bottom:.6rem;font-style:italic">Upload your dataset</div>
        """, unsafe_allow_html=True)

        up = st.file_uploader("", type="csv", label_visibility="collapsed")
        if up:
            df = load_df(up.read())
            _ex = st.session_state.df
            if _ex is None or len(df) != len(_ex):
                st.session_state.df = df
                st.session_state.trained = False
            st.markdown(f"""
            <div style="font-family:'DM Mono',monospace;font-size:.7rem;
                        color:#00ffb3;margin-top:.5rem">
              ✓ {len(df):,} records loaded
            </div>""", unsafe_allow_html=True)
        else:
            if st.session_state.df is None:
                st.markdown("""
                <div style="font-family:'DM Mono',monospace;font-size:.68rem;
                            color:#3a4e65;margin-top:.4rem">Upload CSV to begin</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="font-family:'DM Mono',monospace;font-size:.7rem;
                            color:#00ffb3;margin-top:.5rem">
                  ✓ {len(st.session_state.df):,} records active
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════
def page_dashboard():
    hero("Analytics Overview", "Executive", "Dashboard",
         "Real-time campaign performance intelligence across all channels and segments.")

    df = st.session_state.df
    if df is None:
        st.markdown("""<div class="empty">
          <div class="empty-icon">◈</div>
          <div class="empty-text">Upload your dataset via the sidebar to view the dashboard</div>
        </div>""", unsafe_allow_html=True)
        return

    df2 = parse_cost(df)
    if "Engagement_Score" not in df2.columns:
        df2["Engagement_Score"] = 5.0

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Spend",     f"${df2['Acquisition_Cost'].sum()/1e6:.1f}M",
                 "↑ All campaigns combined", "💰", "cyan")
    with c2: kpi("Average ROI",     f"{df2['ROI'].mean():.2f}%",
                 f"Peak {df2['ROI'].max():.1f}%", "📈", "purple")
    with c3: kpi("Total Campaigns", f"{len(df2):,}",
                 "Full dataset", "🎯", "green")
    with c4: kpi("Avg Engagement",  f"{df2['Engagement_Score'].mean():.1f}/10",
                 f"Avg {df2['Clicks'].mean():,.0f} clicks", "⚡", "gold")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1
    col_a, col_b = st.columns([3, 2])
    with col_a:
        sh("Budget vs ROI by Campaign Type", "Scatter")
        s = df2.sample(min(4000, len(df2)), random_state=1)
        fig = px.scatter(s, x="Acquisition_Cost", y="ROI", color="Campaign_Type",
                         size="Clicks", size_max=15, opacity=0.72,
                         labels={"Acquisition_Cost":"Spend ($)","ROI":"ROI (%)"},
                         color_discrete_sequence=["#00e5ff","#9b59ff","#00ffb3","#ffcc00","#ff4757"])
        fig.update_layout(**PL, height=330)
        fig.update_traces(marker=dict(line=dict(width=0)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    with col_b:
        sh("Avg ROI by Channel", "Ranked")
        ch = df2.groupby("Channel_Used")["ROI"].mean().reset_index().sort_values("ROI")
        fig2 = go.Figure(go.Bar(
            x=ch["ROI"], y=ch["Channel_Used"], orientation="h",
            marker=dict(
                color=ch["ROI"],
                colorscale=[[0,"#1c2a3e"],[0.4,"#00e5ff"],[1,"#9b59ff"]],
                line=dict(width=0)
            ),
            text=ch["ROI"].round(2), textposition="outside",
            textfont=dict(size=10, color="#7a90b0"),
        ))
        fig2.update_layout(**PL, height=330, xaxis_title="Avg ROI (%)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

    # Row 2
    col_c, col_d, col_e = st.columns(3)
    with col_c:
        sh("ROI Distribution")
        fig3 = go.Figure(go.Histogram(x=df2["ROI"], nbinsx=50,
            marker=dict(color="#00e5ff", opacity=0.8, line=dict(width=0))))
        fig3.add_vline(x=df2["ROI"].mean(), line_dash="dash", line_color="#ffcc00",
                       annotation_text="mean", annotation_font=dict(color="#ffcc00", size=10))
        fig3.update_layout(**PL, height=250, xaxis_title="ROI (%)", yaxis_title="Count")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    with col_d:
        sh("Campaign Mix")
        ct = df2["Campaign_Type"].value_counts().reset_index()
        fig4 = go.Figure(go.Pie(
            labels=ct["Campaign_Type"], values=ct["count"], hole=0.62,
            marker=dict(colors=["#00e5ff","#9b59ff","#00ffb3","#ffcc00","#ff4757"],
                        line=dict(color="#07090f", width=2)),
            textinfo="label+percent",
            textfont=dict(family="DM Mono", size=10, color="#7a90b0"),
        ))
        fig4.update_layout(**PL, height=250, showlegend=False,
            annotations=[dict(text="MIX", x=0.5, y=0.5, showarrow=False,
                              font=dict(family="DM Mono", size=10, color="#3a4e65"))])
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})

    with col_e:
        sh("Engagement Score vs ROI")
        eng = df2.groupby("Engagement_Score")["ROI"].mean().reset_index()
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(x=eng["Engagement_Score"], y=eng["ROI"],
            mode="lines+markers",
            line=dict(color="#9b59ff", width=2.5),
            marker=dict(color="#00e5ff", size=8, line=dict(color="#07090f", width=1.5)),
            fill="tozeroy", fillcolor="rgba(155,89,255,0.07)"))
        fig5.update_layout(**PL, height=250,
                           xaxis_title="Engagement Score", yaxis_title="Avg ROI (%)")
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar":False})

    # Spend Trend — only when Date column exists
    if "Date" in df2.columns:
        sh("Monthly Spend Trend", "Time Series")
        df_t = df2.copy()
        df_t["Date"] = pd.to_datetime(df_t["Date"], errors="coerce")
        df_t = df_t.dropna(subset=["Date"])
        if len(df_t) > 0:
            monthly = df_t.groupby(df_t["Date"].dt.to_period("M")).agg(
                Spend=("Acquisition_Cost","sum"), ROI=("ROI","mean")).reset_index()
            monthly["Date"] = monthly["Date"].astype(str)
            fig6 = make_subplots(specs=[[{"secondary_y": True}]])
            fig6.add_trace(go.Bar(x=monthly["Date"], y=monthly["Spend"],
                name="Total Spend", marker=dict(color="#00e5ff", opacity=0.6, line=dict(width=0))),
                secondary_y=False)
            fig6.add_trace(go.Scatter(x=monthly["Date"], y=monthly["ROI"],
                name="Avg ROI", mode="lines+markers",
                line=dict(color="#ffcc00", width=2),
                marker=dict(color="#ff7f50", size=5)),
                secondary_y=True)
            fig6.update_layout(**PL, height=280)
            fig6.update_yaxes(title_text="Spend ($)", secondary_y=False,
                              gridcolor="#1c2a3e", linecolor="#1c2a3e")
            fig6.update_yaxes(title_text="Avg ROI (%)", secondary_y=True,
                              gridcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar":False})

    # Correlation
    sh("Feature Correlation Matrix", "Pearson r")
    _corr_candidates = ["Acquisition_Cost","ROI","Clicks","Impressions","Engagement_Score","Conversion_Rate"]
    _corr_cols = [c for c in _corr_candidates if c in df2.columns]
    corr = df2[_corr_cols].corr()
    fig7 = px.imshow(corr, text_auto=".2f",
                     color_continuous_scale=[[0,"#ff4757"],[0.5,"#141d2e"],[1,"#00e5ff"]],
                     zmin=-1, zmax=1)
    fig7.update_layout(**PL, height=320)
    fig7.update_traces(textfont=dict(family="DM Mono", size=11))
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar":False})


# ══════════════════════════════════════════════════════════════════════
# PAGE 2 — DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════
def page_explorer():
    hero("Preprocessing Pipeline", "Data", "Explorer",
         "Inspect raw data, manual preprocessing steps, and engineered features.")

    df = parse_cost(st.session_state.df)
    if df is None:
        st.warning("Upload the dataset via the sidebar.")
        return

    tab1, tab2, tab3 = st.tabs(["  Raw Data  ", "  Preprocessing  ", "  Feature Engineering  "])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows",    f"{len(df):,}")
        c2.metric("Columns", len(df.columns))
        c3.metric("Missing", int(df.isnull().sum().sum()))
        c4.metric("Channels", df["Channel_Used"].nunique())

        sh(f"Raw Dataset — First 500 of {len(df):,} rows")
        st.dataframe(df.head(500), use_container_width=True, height=320)

        sh("Schema & Data Types")
        col_a, col_b = st.columns(2)
        with col_a:
            st.dataframe(pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Nulls": df.isnull().sum().values,
                "Unique": [df[c].nunique() for c in df.columns],
            }), use_container_width=True, hide_index=True)
        with col_b:
            st.dataframe(df.select_dtypes(include=np.number).describe().round(3),
                         use_container_width=True)

    with tab2:
        steps = [
            ("01","Missing Value Imputation",
             "Numerical columns → Mean  |  Categorical columns → Mode",
             "Pure pandas/numpy — no sklearn SimpleImputer"),
            ("02","Cost Column Parsing",
             'Strips "$" and "," characters, then casts string to float64',
             '"$16,174.00"  →  16174.0'),
            ("03","One-Hot Encoding",
             "Manual binary column creation for Channel_Used & Campaign_Type",
             "Categories stored at fit-time, aligned at transform-time"),
            ("04","Z-Score Normalization",
             "X_scaled = (X − μ) / σ  — fit on training set only",
             "Epsilon 1e-8 prevents division by zero on constant features"),
            ("05","Train / Test Split",
             "80% train / 20% test via deterministic shuffle (seed = 42)",
             "np.random.default_rng().permutation — no sklearn"),
        ]
        for num, title, desc, code in steps:
            st.markdown(f"""
            <div class="step">
              <div class="step-num">{num}</div>
              <div>
                <div class="step-title">{title}</div>
                <div class="step-desc">{desc}</div>
                <div class="step-code">{code}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        sh("Before vs After Z-Score Normalization")
        df2 = parse_cost(df)
        _z_candidates = ["Acquisition_Cost","Clicks","Impressions"]
        _z_cols = [c for c in _z_candidates if c in df2.columns]
        raw = df2[_z_cols].head(300)
        scaled = (raw - raw.mean()) / (raw.std() + 1e-8)
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=["Before Scaling","After Z-Score"])
        clrs = ["#00e5ff","#9b59ff","#00ffb3"]
        for i, col in enumerate(raw.columns):
            fig.add_trace(go.Box(y=raw[col], name=col, marker_color=clrs[i],
                                  line_color=clrs[i], fillcolor="rgba(0,0,0,0)"), row=1, col=1)
            fig.add_trace(go.Box(y=scaled[col], name=col, marker_color=clrs[i],
                                  line_color=clrs[i], fillcolor="rgba(0,0,0,0)",
                                  showlegend=False), row=1, col=2)
        fig.update_layout(**PL, height=320)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        sh("One-Hot Encoding Preview")
        _ohe_cols = [c for c in ["Channel_Used","Campaign_Type"] if c in df.columns]
        ohe = pd.get_dummies(df[_ohe_cols].head(8)).astype(int) if _ohe_cols else pd.DataFrame()
        st.dataframe(ohe, use_container_width=True, hide_index=True)

    with tab3:
        df3 = parse_cost(df)
        # Guard: ensure required columns exist before computing engineered features
        if "Clicks" not in df3.columns:
            df3["Clicks"] = 500
        if "Impressions" not in df3.columns:
            df3["Impressions"] = 5000
        df3["Log_Spend"]       = np.log1p(df3["Acquisition_Cost"])
        df3["Spend_per_Click"] = df3["Acquisition_Cost"] / df3["Clicks"].replace(0,1)
        df3["CTR"]             = df3["Clicks"] / df3["Impressions"].replace(0,1)

        for name, formula, reason in [
            ("Log_Spend",       "log(1 + Acquisition_Cost)", "Compresses right-skewed budget distribution"),
            ("Spend_per_Click", "Acquisition_Cost / Clicks", "Cost efficiency metric per click"),
            ("CTR",             "Clicks / Impressions",      "Click-through rate — engagement proxy"),
        ]:
            st.markdown(f"""
            <div class="feat">
              <div>
                <span class="feat-name">{name}</span>
                <span class="feat-eq">= {formula}</span>
              </div>
              <div class="feat-why">{reason}</div>
            </div>""", unsafe_allow_html=True)

        sh("Engineered Feature Distributions")
        c1, c2, c3 = st.columns(3)
        for cw, feat, clr in [(c1,"Log_Spend","#00e5ff"),
                               (c2,"Spend_per_Click","#9b59ff"),
                               (c3,"CTR","#00ffb3")]:
            fig = go.Figure(go.Histogram(x=df3[feat], nbinsx=40,
                marker=dict(color=clr, opacity=0.8, line=dict(width=0))))
            fig.update_layout(**PL, height=220, xaxis_title=feat, yaxis_title="")
            cw.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        sh("Sample Engineered Data", f"First 20 rows")
        st.dataframe(df3[["Acquisition_Cost","Log_Spend","Spend_per_Click","CTR","ROI"]].head(20),
                     use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE 3 — AI ROI PREDICTOR
# ══════════════════════════════════════════════════════════════════════
def page_predictor():
    hero("Neural Network Inference", "AI ROI", "Predictor",
         "Configure campaign parameters and receive an instant prediction from the trained neural engine.")

    df = st.session_state.df
    if df is None:
        st.warning("Upload the dataset via the sidebar first.")
        return

    # Auto-train on first visit — use raw df, processor handles all cleaning
    if not st.session_state.trained:
        with st.spinner("⚙ Training neural engine… (this takes ~30 seconds)"):
            proc = DataProcessor()
            # Cap at 20k for speed; enough for a strong model
            _train_df = df.sample(min(20000, len(df)), random_state=42)
            X_tr, X_te, y_tr, y_te = proc.fit_transform(_train_df)
            model = ScratchNeuralNet(n_features=X_tr.shape[1], lr=0.01)
            model.train(X_tr, y_tr, X_te, y_te, epochs=120, batch_size=256)
            y_pred = model.predict(X_te)
            st.session_state.update({
                "processor":proc, "model":model,
                "X_train":X_tr, "X_test":X_te, "y_train":y_tr, "y_test":y_te,
                "y_pred_test":y_pred, "loss_history":model.loss_history,
                "val_loss_history":model.val_loss_history, "trained":True,
            })

    proc  = st.session_state.processor
    model = st.session_state.model
    avg   = float(df["ROI"].mean()) if "ROI" in df.columns else 5.0
    df2   = parse_cost(df)  # parsed version for charts only

    sh("Campaign Configuration", "Input Parameters")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            budget   = st.slider("💰 Budget ($)", 5000, 25000, 12000, 500, format="$%d")
            platform = st.selectbox("📡 Channel", sorted(proc.platform_categories_))
        with r1c2:
            clicks        = st.number_input("🖱️ Expected Clicks",    50, 10000, 500, 50)
            campaign_type = st.selectbox("🎯 Campaign Type", sorted(proc.campaign_categories_))

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            impressions = st.number_input("👁️ Impressions", 1000, 15000, 5000, 100)
        with r2c2:
            engagement  = st.slider("⚡ Engagement Score", 1, 10, 5)

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("◈  Run Prediction", type="primary", use_container_width=True)

    with col_r:
        if run:
            X_in = proc.transform_single({
                "Acquisition_Cost": budget, "Channel_Used": platform,
                "Campaign_Type": campaign_type, "Clicks": clicks,
                "Impressions": impressions, "Engagement_Score": engagement,
                "Conversion_Rate": 0.08,
            })
            roi   = max(1.5, min(float(model.predict(X_in)[0]), 10.0))
            delta = roi - avg
            sign  = "+" if delta >= 0 else ""

            if   roi >= 6.5: bcls, btxt = "badge-hi",  "● High Performer"
            elif roi >= 3.5: bcls, btxt = "badge-mid", "● Average"
            else:            bcls, btxt = "badge-lo",  "● Below Average"

            st.markdown(f"""
            <div class="pred-wrap">
              <div class="pred-lbl">Predicted ROI</div>
              <div class="pred-num">{roi:.2f}<span style="font-size:2.2rem;opacity:.5">%</span></div>
              <div class="pred-delta">{sign}{delta:.2f}% vs dataset average ({avg:.2f}%)</div>
              <span class="badge {bcls}">{btxt}</span>
            </div>""", unsafe_allow_html=True)

            # Gauge
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=roi,
                number=dict(suffix="%",
                            font=dict(family="Times New Roman, Georgia, serif",
                                      size=30, color="#f0f4ff")),
                gauge=dict(
                    axis=dict(range=[0,10],
                              tickfont=dict(family="DM Mono", size=9, color="#3a4e65")),
                    bar=dict(color="#00e5ff", thickness=0.28),
                    bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    steps=[
                        dict(range=[0,   3.5], color="rgba(255,71,87,0.1)"),
                        dict(range=[3.5, 6.5], color="rgba(255,204,0,0.1)"),
                        dict(range=[6.5, 10],  color="rgba(0,255,179,0.1)"),
                    ],
                    threshold=dict(line=dict(color="#9b59ff", width=2.5),
                                   thickness=0.85, value=avg),
                ),
            ))
            fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=230,
                                font=dict(family="DM Mono", color="#7a90b0"),
                                margin=dict(l=20,r=20,t=15,b=10))
            st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar":False})

            tips = {
                "badge-hi":  "Strong projection — consider scaling budget for this configuration.",
                "badge-mid": "Solid baseline. Refine targeting or boost engagement to push higher.",
                "badge-lo":  "Below average. Try a different channel or increase click volume.",
            }
            st.info(f"**Insight —** {tips[bcls]}")

        else:
            st.markdown("""
            <div class="empty" style="height:280px;display:flex;flex-direction:column;
                 align-items:center;justify-content:center">
              <div class="empty-icon">◈</div>
              <div class="empty-text">Configure parameters on the left<br>then click Run Prediction</div>
            </div>""", unsafe_allow_html=True)

    # Channel benchmark (shown after prediction)
    if run:
        sh("Channel ROI Benchmark", "vs Your Prediction")
        df2    = parse_cost(df)
        ch_avg = df2.groupby("Channel_Used")["ROI"].mean().reset_index()
        colors = ["#00e5ff" if c == platform else "#1c2a3e" for c in ch_avg["Channel_Used"]]
        fig_ch = go.Figure(go.Bar(
            x=ch_avg["Channel_Used"], y=ch_avg["ROI"],
            marker=dict(color=colors, line=dict(width=0)),
            text=ch_avg["ROI"].round(2), textposition="outside",
            textfont=dict(family="DM Mono", size=10, color="#7a90b0"),
        ))
        fig_ch.add_hline(y=roi, line_dash="dash", line_color="#9b59ff", line_width=1.5,
                         annotation_text=f"Prediction: {roi:.2f}%",
                         annotation_font=dict(family="DM Mono", size=10, color="#9b59ff"))
        fig_ch.update_layout(**PL, height=260, yaxis_title="Avg ROI (%)", xaxis_title="")
        st.plotly_chart(fig_ch, use_container_width=True, config={"displayModeBar":False})


# ══════════════════════════════════════════════════════════════════════
# PAGE 4 — NEURAL LAB
# ══════════════════════════════════════════════════════════════════════
def page_neural_lab():
    hero("Model Training & Evaluation", "Neural", "Lab",
         "Live training curves, performance metrics, and architectural deep-dive.")

    df = st.session_state.df
    if df is None:
        st.warning("Upload the dataset via the sidebar.")
        return

    sh("Training Configuration", "Hyperparameters")
    c1, c2, c3, c4 = st.columns(4)
    epochs   = c1.slider("Epochs",        20, 200, 80, 10)
    lr       = c2.select_slider("Learning Rate", [0.0001,0.001,0.005,0.01,0.05], 0.005)
    batch_sz = c3.select_slider("Batch Size",    [128,256,512,1024], 256)
    _max_rows = len(df)
    _min_rows = min(100, _max_rows)
    _def_rows = min(2000, _max_rows)
    _step     = max(1, _min_rows)
    n_rows    = c4.slider("Training Samples", _min_rows, _max_rows, _def_rows, _step) if _max_rows > _min_rows else _max_rows

    train_btn = st.button("⬟  Train Neural Network", type="primary")

    if train_btn:
        proc = DataProcessor()
        with st.spinner("Preprocessing…"):
            _safe_n = min(n_rows, len(df))
            X_tr, X_te, y_tr, y_te = proc.fit_transform(df.sample(_safe_n, random_state=42))
        model = ScratchNeuralNet(n_features=X_tr.shape[1], lr=lr)

        sh("Live Loss Curve", "Training in Progress")
        chart_ph = st.empty()
        prog     = st.progress(0)
        stat_ph  = st.empty()
        tl_list, vl_list = [], []

        def cb(epoch, tl, vl):
            tl_list.append(tl); vl_list.append(vl)
            prog.progress(epoch / epochs)
            stat_ph.markdown(
                f'<div style="font-family:\'DM Mono\',monospace;font-size:.75rem;'
                f'color:#3a4e65;margin:.3rem 0">'
                f'Epoch <span style="color:#f0f4ff">{epoch}/{epochs}</span>  ·  '
                f'Train <span style="color:#00e5ff">{tl:.4f}</span>  ·  '
                f'Val <span style="color:#9b59ff">{vl:.4f}</span></div>',
                unsafe_allow_html=True)
            if epoch % max(1, epochs // 25) == 0 or epoch == epochs:
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=tl_list, mode="lines", name="Train Loss",
                    line=dict(color="#00e5ff", width=2.5),
                    fill="tozeroy", fillcolor="rgba(0,229,255,0.05)"))
                fig.add_trace(go.Scatter(y=vl_list, mode="lines", name="Val Loss",
                    line=dict(color="#9b59ff", width=2, dash="dash")))
                fig.update_layout(**PL, height=290,
                                  xaxis_title="Epoch", yaxis_title="MSE Loss")
                chart_ph.plotly_chart(fig, use_container_width=True,
                                      config={"displayModeBar":False})

        model.train(X_tr, y_tr, X_te, y_te, epochs=epochs,
                    batch_size=batch_sz, progress_callback=cb)
        y_pred = model.predict(X_te)
        st.session_state.update({
            "processor":proc, "model":model,
            "X_train":X_tr, "X_test":X_te, "y_train":y_tr, "y_test":y_te,
            "y_pred_test":y_pred, "loss_history":tl_list,
            "val_loss_history":vl_list, "trained":True,
        })
        prog.empty(); stat_ph.empty()
        st.success("◈  Training complete — metrics updated below.")

    if st.session_state.trained:
        model  = st.session_state.model
        y_te   = st.session_state.y_test
        y_pred = st.session_state.y_pred_test
        tl     = st.session_state.loss_history
        vl     = st.session_state.val_loss_history

        sh("Performance Metrics", "Test Set")
        r2   = ScratchNeuralNet.r2_score(y_te, y_pred)
        mae  = ScratchNeuralNet.mae(y_te, y_pred)
        mse  = ScratchNeuralNet.mse(y_te, y_pred)
        rmse = float(np.sqrt(mse))
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("R² Score", f"{r2:.4f}", help="1.0 = perfect fit")
        m2.metric("MAE",      f"{mae:.4f}")
        m3.metric("MSE",      f"{mse:.4f}")
        m4.metric("RMSE",     f"{rmse:.4f}")

        sh("Training Curves & Prediction Quality")
        pa, pb = st.columns(2)
        with pa:
            fig_l = go.Figure()
            fig_l.add_trace(go.Scatter(y=tl, mode="lines", name="Train Loss",
                line=dict(color="#00e5ff",width=2.5),
                fill="tozeroy", fillcolor="rgba(0,229,255,0.05)"))
            fig_l.add_trace(go.Scatter(y=vl, mode="lines", name="Val Loss",
                line=dict(color="#9b59ff",width=2,dash="dash")))
            fig_l.update_layout(**PL, height=310,
                                xaxis_title="Epoch", yaxis_title="MSE Loss")
            st.plotly_chart(fig_l, use_container_width=True, config={"displayModeBar":False})

        with pb:
            idx = np.random.choice(len(y_te), size=min(800,len(y_te)), replace=False)
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=y_te[idx], y=y_pred[idx], mode="markers",
                marker=dict(color="#9b59ff",size=5,opacity=0.65,line=dict(width=0)),
                name="Predictions"))
            mn = min(y_te.min(), y_pred.min())
            mx = max(y_te.max(), y_pred.max())
            fig_p.add_trace(go.Scatter(x=[mn,mx], y=[mn,mx], mode="lines",
                line=dict(color="#00e5ff",dash="dash",width=1.5), name="Perfect Fit"))
            fig_p.update_layout(**PL, height=310,
                                xaxis_title="Actual ROI", yaxis_title="Predicted ROI")
            st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar":False})

        sh("Residual Distribution", "Error Analysis")
        res = y_pred - y_te
        fig_r = go.Figure(go.Histogram(x=res, nbinsx=60,
            marker=dict(color="#00ffb3", opacity=0.75, line=dict(width=0))))
        fig_r.add_vline(x=0, line_dash="dash", line_color="#ff4757", line_width=1.5)
        fig_r.add_vline(x=res.mean(), line_dash="dot", line_color="#ffcc00", line_width=1.5,
            annotation_text=f"μ = {res.mean():.3f}",
            annotation_font=dict(family="DM Mono", size=10, color="#ffcc00"))
        fig_r.update_layout(**PL, height=250,
                            xaxis_title="Residual (Predicted − Actual)", yaxis_title="Count")
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar":False})

        sh("Network Architecture", "Layer Details")
        n_f = st.session_state.X_train.shape[1]
        st.markdown(f"""
        <table class="arch">
          <tr><th>Layer</th><th>Neurons</th><th>Activation</th><th>Parameters</th></tr>
          <tr><td>Input</td><td>{n_f}</td>
              <td><span class="atag atag-none">—</span></td><td style="color:#3a4e65">—</td></tr>
          <tr><td>Hidden 1</td><td>16</td>
              <td><span class="atag atag-relu">ReLU</span></td>
              <td>W({n_f}×16) + b(16) = {n_f*16+16:,} params</td></tr>
          <tr><td>Hidden 2</td><td>8</td>
              <td><span class="atag atag-relu">ReLU</span></td>
              <td>W(16×8) + b(8) = 136 params</td></tr>
          <tr><td>Output</td><td>1</td>
              <td><span class="atag atag-lin">Linear</span></td>
              <td>W(8×1) + b(1) = 9 params &nbsp;·&nbsp;
                  <strong>Total: {n_f*16+16+128+8+8+1:,}</strong></td></tr>
        </table>""", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty">
          <div class="empty-icon">⬟</div>
          <div class="empty-text">Configure hyperparameters above and click<br>Train Neural Network to begin</div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════
sidebar()
p = st.session_state.page
if   p == "dashboard": page_dashboard()
elif p == "explorer":  page_explorer()
elif p == "predictor": page_predictor()
elif p == "lab":       page_neural_lab()
