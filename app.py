import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path

st.set_page_config(
    page_title="Aurora Finance",
    layout="wide"
)

# -----------------------------
# Styling
# -----------------------------

st.markdown("""
<style>
.stApp {
    background-color: #f4f6f9;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

h1 {
    color: #111827;
    font-weight: 800;
    letter-spacing: -0.5px;
}

h2, h3, h4 {
    color: #1f2937;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5e7eb;
    padding: 18px 20px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
}

div[data-testid="stMetricLabel"] {
    font-size: 13px;
    color: #6b7280;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    font-size: 26px;
    color: #111827;
    font-weight: 800;
}

div[data-testid="stPlotlyChart"] {
    background: white;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
}

div[data-testid="stDataFrame"] {
    background: white;
    padding: 14px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
}

div[data-testid="stAlert"] {
    border-radius: 14px;
}

hr {
    border: none;
    height: 1px;
    background-color: #d1d5db;
    margin: 24px 0;
}
            
.matrix-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 14px;
    width: 100%;
}

.matrix-box {
    border-radius: 14px;
    padding: 18px;
    min-height: 115px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border: 1px solid #e5e7eb;
    box-sizing: border-box;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Helper functions
# -----------------------------

def clean_money(series):
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .replace("nan", "0")
        .replace("", "0")
        .astype(float)
    )

def clean_percent(series):
    return (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .replace("nan", "0")
        .replace("", "0")
        .astype(float) / 100
    )

def load_csv_safe(file_name):
    if Path(file_name).exists():
        return pd.read_csv(file_name)
    return pd.DataFrame()

def polish_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=13, color="#111827"),
        title_font=dict(size=18, color="#111827"),
        margin=dict(l=30, r=30, t=60, b=30),
        legend_title_text=""
    )
    return fig


# -----------------------------
# Load datasets
# -----------------------------

corp = load_csv_safe("module1\\module1_ranked_projects.csv")
loans = load_csv_safe("module 2\\aurora_loan_portfolio_scored.csv")
fraud = load_csv_safe("module 2\\aurora_fraud_alerts.csv")


# -----------------------------
# Clean Corporate Finance Data
# -----------------------------

if not corp.empty:
    for col in ["Investment_Cost", "NPV", "Predicted_NPV", "Expected_Value"]:
        if col in corp.columns:
            corp[col] = clean_money(corp[col])

    if "Predicted_Success_Probability" in corp.columns:
        corp["Predicted_Success_Probability"] = clean_percent(
            corp["Predicted_Success_Probability"]
        )

    if "Risk_Encoded" in corp.columns and "Project_Risk" not in corp.columns:
        corp["Project_Risk"] = corp["Risk_Encoded"].map({1: "Low", 2: "Medium", 3: "High"}).fillna("Unknown")


# -----------------------------
# Clean Banking Data
# -----------------------------

if not loans.empty:
    if "Loan_Amount" in loans.columns:
        loans["Loan_Amount"] = clean_money(loans["Loan_Amount"])

    if "Annual_Income" in loans.columns:
        loans["Annual_Income"] = clean_money(loans["Annual_Income"])

    if "PD" in loans.columns:
        loans["PD"] = loans["PD"].astype(float)

if not fraud.empty:
    if "Amount" in fraud.columns:
        fraud["Amount"] = clean_money(fraud["Amount"])

    if "Fraud_Risk_Score" in fraud.columns:
        fraud["Fraud_Risk_Score"] = fraud["Fraud_Risk_Score"].astype(float)


# -----------------------------
# Sidebar navigation
# -----------------------------

st.sidebar.title("Aurora Finance")
st.sidebar.caption("Executive Decision Intelligence")

selected_tab = st.sidebar.radio(
    "Select Module",
    [
        "Executive Summary",
        "Corporate Finance",
        "Banking",
        "Financial Markets",
        "Derivatives"
    ]
)

# =====================================================
# Executive Summary
# =====================================================

if selected_tab == "Executive Summary":
    st.title("Aurora Finance Executive Summary")
    st.caption("AI-powered decision intelligence across corporate finance, banking, markets, and derivatives.")

    if not corp.empty:
        funded = corp[corp["Recommendation"] == "Fund"]
        corp_funded_count = len(funded)
        corp_predicted_npv = funded["Predicted_NPV"].sum()
        corp_total_investment = funded["Investment_Cost"].sum()
    else:
        corp_funded_count = 0
        corp_predicted_npv = 0
        corp_total_investment = 0

    if not loans.empty:
        high_risk_loans = loans[loans["Risk_Tier"].isin(["High Risk", "Very High Risk"])]
        high_risk_count = len(high_risk_loans)
        high_risk_exposure = high_risk_loans["Loan_Amount"].sum()
    else:
        high_risk_count = 0
        high_risk_exposure = 0

    if not fraud.empty:
        fraud_alerts = len(fraud)
        fraud_exposure = fraud["Amount"].sum()
    else:
        fraud_alerts = 0
        fraud_exposure = 0

    st.markdown("## Aurora Finance Module Overview")

    with st.container(border=True):
        st.subheader("Corporate Finance")
        st.caption("Project funding optimization and capital allocation decisions.")

        c1, c2, c3 = st.columns(3)

        c1.metric("Projects Funded", corp_funded_count)
        c2.metric("Predicted Portfolio NPV", f"${corp_predicted_npv:,.0f}")
        c3.metric("Approved Investment", f"${corp_total_investment:,.0f}")

    with st.container(border=True):
        st.subheader("Banking")
        st.caption("Credit risk monitoring and fraud exposure intelligence.")

        b1, b2, b3 = st.columns(3)

        b1.metric("High-Risk Loans", high_risk_count)
        b2.metric("Risk Exposure", f"${high_risk_exposure:,.0f}")
        b3.metric("Fraud Exposure", f"${fraud_exposure:,.0f}")

    with st.container(border=True):
        st.subheader("Financial Markets")
        st.caption("Market prediction, portfolio analytics, and trading signal intelligence.")

        f1, f2, f3 = st.columns(3)

        f1.metric("Portfolio Return", "Coming Soon")
        f2.metric("Market Risk Score", "Coming Soon")
        f3.metric("Signal Accuracy", "Coming Soon")

    # Load derivatives metrics for summary — fall back to last known values
    _dm_path = Path("outputs/module4_metrics.json")
    if _dm_path.exists():
        with open(_dm_path) as _f:
            _dm = json.load(_f)
    else:
        _dm = {
            "port_delta": -2327.5,
            "var_95":     -100605,
            "best_rmse":  18.0652,
            "bs_improvement_pct": 55.9,
        }
    _deriv_delta   = f"{_dm['port_delta']:,.1f}"
    _deriv_var95   = f"₹{abs(_dm['var_95']):,.0f}"
    _deriv_ml_rmse = f"₹{_dm['best_rmse']:.2f}"

    with st.container(border=True):
        st.subheader("Derivatives")
        st.caption("Option pricing, Greeks monitoring, and hedge performance analytics.")

        d1, d2, d3 = st.columns(3)

        d1.metric("Portfolio Delta",    _deriv_delta,   "Net directional exposure")
        d2.metric("VaR (95%)",          _deriv_var95,   "Max expected daily loss")
        d3.metric("Best ML RMSE",       _deriv_ml_rmse, "vs B-S benchmark")

    st.divider()

    _deriv_status    = "Active"
    _deriv_kpi_label = _deriv_var95

    summary_data = pd.DataFrame({
        "Module": [
            "Corporate Finance",
            "Banking",
            "Financial Markets",
            "Derivatives"
        ],
        "Primary KPI": [
            f"${corp_predicted_npv:,.0f}",
            f"${high_risk_exposure:,.0f}",
            "Pending Data",
            _deriv_kpi_label
        ],
        "Decision Focus": [
            "Project funding and capital allocation",
            "Credit risk and fraud monitoring",
            "Market signals and portfolio performance",
            "Option pricing, delta hedging and portfolio VaR"
        ],
        "Status": [
            "Active",
            "Active",
            "Pending Data",
            _deriv_status
        ]
    })

    st.subheader("Executive Module Status Report")
    st.dataframe(summary_data, width="stretch", hide_index=True)
# =====================================================
# Corporate Finance
# =====================================================

elif selected_tab == "Corporate Finance":
    st.markdown("""
    <style>
    .section-label {
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1.2px;
        color: #6b7280;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .dashboard-header {
        background: #f3f4f6;
        padding: 26px 28px;
        border-radius: 0px;
        margin-bottom: 22px;
    }

    .dashboard-title {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 4px;
    }

    .dashboard-subtitle {
        font-size: 16px;
        color: #6b7280;
        font-weight: 600;
    }

    .shap-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        min-height: 360px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }

    .matrix-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        min-height: 390px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }

    .matrix-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 16px;
    }

    .matrix-box {
        border-radius: 14px;
        padding: 18px;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid #e5e7eb;
    }

    .matrix-title {
        font-size: 14px;
        font-weight: 700;
        color: #374151;
    }

    .matrix-value {
        font-size: 28px;
        font-weight: 900;
        color: #111827;
        margin-top: 4px;
    }

    .matrix-subtitle {
        font-size: 13px;
        color: #6b7280;
        margin-top: 2px;
    }

    .green-box {
        background: #ecfdf5;
    }

    .yellow-box {
        background: #fffbeb;
    }

    .orange-box {
        background: #fff7ed;
    }

    .red-box {
        background: #fef2f2;
    }
    </style>
    """, unsafe_allow_html=True)

    if corp.empty:
        st.warning("project_output.csv not found in this folder.")
        st.stop()

    recommendation_options = ["All recommendations"] + sorted(
        corp["Recommendation"].dropna().unique().tolist()
    )

    default_rec_index = (
        recommendation_options.index("Fund")
        if "Fund" in recommendation_options
        else 0
    )
    
    # -----------------------------
    # Header
    # -----------------------------

    st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">Capital Allocation Dashboard</div>
        <div class="dashboard-subtitle">Executive summary · Q2 2025 cycle</div>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------
    # Portfolio Snapshot
    # -----------------------------

    st.markdown('<div class="section-label">Portfolio Snapshot</div>', unsafe_allow_html=True)

    filter_col, blank_col = st.columns([1.2, 2.8])

    with filter_col:
        recommendation_filter = st.selectbox(
            "Recommendation Filter",
            recommendation_options,
            index=default_rec_index,
            label_visibility="collapsed",
            key="kpi_recommendation_filter"
        )

    if recommendation_filter != "All recommendations":
        filtered_corp = corp[corp["Recommendation"] == recommendation_filter].copy()
    else:
        filtered_corp = corp.copy()

    selected_projects_count = len(filtered_corp)
    selected_rate = selected_projects_count / len(corp) if len(corp) > 0 else 0

    avg_predicted_npv = (
        filtered_corp["Predicted_NPV"].mean()
        if selected_projects_count > 0 and "Predicted_NPV" in filtered_corp.columns
        else 0
    )

    avg_success_prob = (
        filtered_corp["Predicted_Success_Probability"].mean()
        if selected_projects_count > 0 and "Predicted_Success_Probability" in filtered_corp.columns
        else 0
    )

    total_expected_value = (
        filtered_corp["Expected_Value"].sum()
        if selected_projects_count > 0 and "Expected_Value" in filtered_corp.columns
        else 0
    )

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Projects Selected",
        selected_projects_count,
        f"{selected_rate:.0%} of portfolio"
    )

    k2.metric(
        "Avg. Predicted NPV",
        f"${avg_predicted_npv / 1_000_000:.1f}M",
        f"{recommendation_filter}"
    )

    k3.metric(
        "Avg. Success Probability",
        f"{avg_success_prob:.0%}",
        "Model confidence"
    )

    k4.metric(
        "Total Expected Value",
        f"${total_expected_value / 1_000_000:.1f}M",
        "Selected portfolio"
    )

    st.divider()

    # -----------------------------
    # Results Section
    # -----------------------------

    st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

    results_filter_col, _ = st.columns([1.2, 2.8])

    with results_filter_col:
        results_recommendation_filter = st.selectbox(
            "Results Recommendation Filter",
            recommendation_options,
            index=default_rec_index,
            label_visibility="collapsed",
            key="results_recommendation_filter"
        )

    if results_recommendation_filter != "All recommendations":
        results_df = corp[corp["Recommendation"] == results_recommendation_filter].copy()
    else:
        results_df = corp.copy()

    chart_left, chart_right = st.columns(2)

    with chart_left:
        finance_colors = [
            "#0F172A",  # navy
            "#1E40AF",  # blue
            "#047857",  # green
            "#B45309",  # amber
            "#6B7280"   # grey
        ]
                
        st.markdown("#### Portfolio Allocation by Department")

        if results_df.empty:
            st.info("No projects available for selected recommendation.")
        else:
            dept_alloc = (
                results_df.groupby("Department", as_index=False)["Investment_Cost"]
                .sum()
                .sort_values("Investment_Cost", ascending=False)
            )

            fig = px.pie(
                dept_alloc,
                names="Department",
                values="Investment_Cost",
                title=f"Department Allocation · {results_recommendation_filter}",
                color_discrete_sequence=finance_colors
            )

            fig.update_layout(
                template="plotly_white",
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(size=13),
                title_font=dict(size=17),
                margin=dict(l=20, r=20, t=60, b=20),
                legend_title_text=""
            )
            st.plotly_chart(fig, width="stretch")

    with chart_right:
        st.markdown("#### Risk vs. NPV Matrix")
        st.caption("Project count by risk and value profile")

        if results_df.empty:
            st.info("No projects available for selected recommendation.")
        else:
            npv_threshold = results_df["Predicted_NPV"].median()

            low_risk_values = ["Low", "Medium"]
            high_risk_values = ["High"]

            low_risk_high_npv = len(results_df[
                (results_df["Project_Risk"].isin(low_risk_values)) &
                (results_df["Predicted_NPV"] >= npv_threshold)
            ])

            low_risk_low_npv = len(results_df[
                (results_df["Project_Risk"].isin(low_risk_values)) &
                (results_df["Predicted_NPV"] < npv_threshold)
            ])

            high_risk_high_npv = len(results_df[
                (results_df["Project_Risk"].isin(high_risk_values)) &
                (results_df["Predicted_NPV"] >= npv_threshold)
            ])

            high_risk_low_npv = len(results_df[
                (results_df["Project_Risk"].isin(high_risk_values)) &
                (results_df["Predicted_NPV"] < npv_threshold)
            ])

            q1, q2 = st.columns(2)
            q3, q4 = st.columns(2)

            with q1:
                st.metric("Low Risk · High NPV", low_risk_high_npv, "Priority candidates")

            with q2:
                st.metric("Low Risk · Low NPV", low_risk_low_npv, "Safe but lower value")

            with q3:
                st.metric("High Risk · High NPV", high_risk_high_npv, "Monitor closely")

            with q4:
                st.metric("High Risk · Low NPV", high_risk_low_npv, "Avoid / reject")

    # -----------------------------
    # SHAP Explanation
    # -----------------------------
    st.markdown('<div class="section-label">Model Decision Explanation (SHAP)</div>', unsafe_allow_html=True)

    shap_left, shap_right = st.columns(2)

    with shap_left:
        with st.container(border=True):
            st.subheader("Global Feature Importance")
            st.caption("Average SHAP contribution across all projects")

            shap_summary_path = "module1/01_shap_summary_regression.png"

            if Path(shap_summary_path).exists():
                st.image(shap_summary_path, use_container_width=True)
            else:
                st.warning("SHAP summary image not found: module1/01_shap_summary_regression.png")

    with shap_right:
        top_project = corp.sort_values("Rank").iloc[0]

        with st.container(border=True):
            st.subheader(f"Top Project Breakdown · PRJ-{top_project['Project_ID']} (Rank #1)")
            st.caption("Why this project scored highest — per-feature direction")

            shap_top_project_path = "module1/03_shap_waterfall_regression_project_43.png"

            if Path(shap_top_project_path).exists():
                st.image(shap_top_project_path, use_container_width=True)
            else:
                st.warning("SHAP waterfall image not found: module1/03_shap_waterfall_regression_project_43.png")

    # -----------------------------
    # Ranked Project List
    # -----------------------------

    st.markdown('<div class="section-label">Ranked Project List</div>', unsafe_allow_html=True)

    search_col, rec_col, dept_col, risk_col = st.columns([2.4, 1.1, 1.1, 1.1])

    with search_col:
        search_text = st.text_input(
            "Search",
            placeholder="Search by project ID, department...",
            label_visibility="collapsed"
        )

    with rec_col:
        rec_filter = st.selectbox(
            "Recommendation",
            ["All recommendations"] + sorted(corp["Recommendation"].dropna().unique().tolist()),
            label_visibility="collapsed",
            key="table_recommendation_filter"
        )

    with dept_col:
        dept_filter = st.selectbox(
            "Department",
            ["All departments"] + sorted(corp["Department"].dropna().unique().tolist()),
            label_visibility="collapsed"
        )

    with risk_col:
        risk_filter = st.selectbox(
            "Risk",
            ["All risk levels"] + sorted(corp["Project_Risk"].dropna().unique().tolist()),
            label_visibility="collapsed"
        )

    table_df = corp.copy()

    if search_text:
        table_df = table_df[
            table_df["Project_ID"].astype(str).str.contains(search_text, case=False, na=False)
            | table_df["Department"].astype(str).str.contains(search_text, case=False, na=False)
        ]

    if rec_filter != "All recommendations":
        table_df = table_df[table_df["Recommendation"] == rec_filter]

    if dept_filter != "All departments":
        table_df = table_df[table_df["Department"] == dept_filter]

    if risk_filter != "All risk levels":
        table_df = table_df[table_df["Project_Risk"] == risk_filter]

    st.caption(f"{len(table_df)} projects")

    display_cols = [
        "Rank",
        "Project_ID",
        "Department",
        "Recommendation",
        "Project_Risk",
        "Investment_Cost",
        "NPV",
        "Predicted_NPV",
        "Predicted_Success_Probability",
        "Historical_ROI",
        "Profitability_Index",
        "Simple_Payback_Period",
        "Priority_Score"
    ]

    display_cols = [col for col in display_cols if col in table_df.columns]

    st.dataframe(
        table_df[display_cols].sort_values("Rank"),
        width="stretch",
        hide_index=True
    )

# =====================================================
# Banking
# =====================================================

elif selected_tab == "Banking":

    st.markdown("""
    <style>
    .section-label {
        font-size: 13px; font-weight: 800; letter-spacing: 1.2px;
        color: #6b7280; text-transform: uppercase; margin-bottom: 10px;
    }
    .dashboard-header  { background:#f3f4f6; padding:26px 28px; border-radius:0px; margin-bottom:22px; }
    .dashboard-title   { font-size:28px; font-weight:800; color:#111827; margin-bottom:4px; }
    .dashboard-subtitle{ font-size:16px; color:#6b7280; font-weight:600; }
    </style>
    """, unsafe_allow_html=True)

    if loans.empty and fraud.empty:
        st.warning("Banking CSV files not found in module 2/.")
        st.stop()

    # ── Pre-compute all metrics ───────────────────────────────────────
    _hr_tiers = ["High Risk", "Very High Risk"]

    if not loans.empty:
        _hr     = loans[loans["Risk_Tier"].isin(_hr_tiers)]
        _reject = loans[loans["Recommended"] == "Reject"]
        _review = loans[loans["Recommended"] == "Review & Monitor"]
        _total_exp    = loans["Loan_Amount"].sum()
        _hr_exp       = _hr["Loan_Amount"].sum()
        _avg_pd       = loans["PD"].mean()
        _confirmed_fraud = int(fraud["Fraud_Flag"].sum()) if not fraud.empty else 0
    else:
        _hr = _reject = _review = pd.DataFrame()
        _total_exp = _hr_exp = _avg_pd = 0
        _confirmed_fraud = 0

    if not fraud.empty:
        _fraud_count    = len(fraud)
        _fraud_exposure = fraud["Amount"].sum()
        _avg_fscore     = fraud["Fraud_Risk_Score"].mean()
    else:
        _fraud_count = _fraud_exposure = _avg_fscore = 0

    # ── Header ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">Banking Risk &amp; Fraud Dashboard</div>
        <div class="dashboard-subtitle">
            Credit risk scoring · Fraud detection · Lending officer decision support
        </div>
    </div>
    """, unsafe_allow_html=True)

    _total_loans = len(loans) if not loans.empty else 0

    # ── LOANS SECTION ────────────────────────────────────────────────
    st.markdown('<div class="section-label">Credit Portfolio</div>', unsafe_allow_html=True)

    def _kpi_card(label, value, context, delta):
        """Metric card with an extra small context line above the delta arrow."""
        return f"""
        <div style="background:white;border:1px solid #e5e7eb;padding:18px 20px;
                    border-radius:16px;box-shadow:0 6px 18px rgba(15,23,42,0.08);">
            <div style="font-size:13px;color:#6b7280;font-weight:600;">{label}</div>
            <div style="font-size:26px;color:#111827;font-weight:800;margin-top:4px;">{value}</div>
            <div style="font-size:11px;color:#9ca3af;margin-top:6px;">{context}</div>
            <div style="font-size:13px;color:#16a34a;font-weight:600;margin-top:2px;">&#8593; {delta}</div>
        </div>"""

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi_card(
            "At-Risk Exposure",
            f"${_hr_exp:,.0f}",
            f"of ${_total_exp:,.0f} total",
            "High + Very High Risk"
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(_kpi_card(
            "Avg Default Prob",
            f"{_avg_pd:.1%}",
            f"across {_total_loans} loans",
            "Portfolio average PD"
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(_kpi_card(
            "Loans to Reject",
            len(_reject),
            f"from {_total_loans} loans",
            "Very High Risk"
        ), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi_card(
            "Under Review",
            len(_review),
            f"from {_total_loans} loans",
            "High Risk — monitor"
        ), unsafe_allow_html=True)

    st.divider()

    # ── Section: Credit Risk Portfolio ───────────────────────────────
    st.markdown('<div class="section-label">Credit Risk Portfolio</div>', unsafe_allow_html=True)

    cr_l, cr_r = st.columns([1, 1])

    with cr_l:
        with st.container(border=True):
            st.subheader("Portfolio Risk Breakdown")
            st.caption("Loan count by risk tier and PD spread within each tier")
            _p = Path("module 2/risk_tiers.png")
            if _p.exists():
                st.image(str(_p), use_container_width=True)
            else:
                st.warning("Run notebook to generate risk_tiers.png")

    with cr_r:
        with st.container(border=True):
            st.subheader("Recommended Lending Actions")
            st.caption("Decision distribution across the full portfolio")
            if not loans.empty and "Recommended" in loans.columns:
                _action_colors = {
                    "Approve":                  "#4CAF50",
                    "Approve with Conditions":  "#FFC107",
                    "Review & Monitor":         "#FF5722",
                    "Reject":                   "#B71C1C",
                }
                _act = loans["Recommended"].value_counts().reset_index()
                _act.columns = ["Action", "Count"]
                fig = px.pie(
                    _act, names="Action", values="Count",
                    color="Action",
                    color_discrete_map=_action_colors,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                fig.update_layout(
                    template="plotly_white", paper_bgcolor="white",
                    showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

    # ── Decision Explainability ───────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-label">Decision Explainability</div>', unsafe_allow_html=True)

    ex_l, ex_r = st.columns(2)

    with ex_l:
        with st.container(border=True):
            st.subheader("What Drives High Credit Risk?")
            st.caption("Mean |SHAP| — top 8 features pushing loans toward high-risk classification")
            _sp = Path("module 2/shap_credit_bar.png")
            if _sp.exists():
                st.image(str(_sp), use_container_width=True)
            else:
                st.warning("Run notebook to generate shap_credit_bar.png")

    with ex_r:
        with st.container(border=True):
            st.subheader("Highest-Risk Loan — Why?")
            st.caption("SHAP waterfall for the single highest-PD loan — use when presenting a reject decision")
            _wp = Path("module 2/shap_waterfall_loan.png")
            if _wp.exists():
                st.image(str(_wp), use_container_width=True)
            else:
                st.warning("Run notebook to generate shap_waterfall_loan.png")

    # ── High-Risk Loan Watchlist ──────────────────────────────────────
    st.divider()
    st.markdown('<div class="section-label">High-Risk Loan Watchlist</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.caption(f"{len(_hr)} loans flagged — High Risk + Very High Risk, sorted by PD descending")
        if not _hr.empty:
            _loan_cols = [c for c in [
                "Loan_ID", "Customer_Type", "Loan_Amount",
                "Debt_to_Income", "PD", "Risk_Tier", "Recommended"
            ] if c in _hr.columns]
            st.dataframe(
                _hr[_loan_cols].sort_values("PD", ascending=False),
                hide_index=True, use_container_width=True
            )

    # ════════════════════════════════════════════════════════════════
    # FRAUD SECTION
    # ════════════════════════════════════════════════════════════════
    st.divider()
    st.markdown('<div class="section-label">Fraud Monitoring</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Alerts Flagged",       _fraud_count,              "Top 10% risk score")
    f2.metric("Confirmed Fraud",      _confirmed_fraud,          "Labelled in dataset")
    f3.metric("Fraud Exposure",       f"${_fraud_exposure:,.0f}")
    f4.metric("Avg Fraud Risk Score", f"{_avg_fscore:.3f}",       "0 = clean · 1 = high risk")

    st.divider()

    # ── Fraud Detection Dashboard ─────────────────────────────────────
    st.markdown('<div class="section-label">Fraud Detection Dashboard</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.caption(
            "Alert composition · Fraud risk score distribution vs actual labels · "
            "Fraud rate by transaction type · Alert timeline"
        )
        _fp = Path("module 2/fraud_dashboard.png")
        if _fp.exists():
            st.image(str(_fp), use_container_width=True)
        else:
            st.warning("Run notebook to generate fraud_dashboard.png")



# =====================================================
# Financial Markets Placeholder
# =====================================================

elif selected_tab == "Financial Markets":
    st.title("Financial Markets")
    st.caption("Placeholder module for market prediction, portfolio analytics, and trading signals.")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Portfolio Return", "Coming Soon")
    c2.metric("Market Risk Score", "Coming Soon")
    c3.metric("Signal Accuracy", "Coming Soon")
    c4.metric("Value at Risk", "Coming Soon")

    st.info(
        "Connect this module later to market prediction outputs such as stock returns, volatility, Sharpe ratio, VaR, and buy/sell signals."
    )


# =====================================================
# Derivatives — Risk Dashboard
# =====================================================

elif selected_tab == "Derivatives":

    # ── Load metrics (fallback to last known notebook output values) ──
    _metrics_path = Path("module 4/module4_metrics.json")
    if _metrics_path.exists():
        with open(_metrics_path) as _f:
            dm = json.load(_f)
    else:
        dm = {
            "nifty_spot": 21927.4,        "dataset_size": 41389,
            "strikes_count": 107,          "expiries_count": 6,
            "best_model": "Random Forest", "best_rmse": 18.0652,
            "bs_improvement_pct": 55.9,
            "port_delta": -2327.5,         "port_gamma": 50.7426,
            "var_95": -100605,             "var_99": -186956,
            "cvar_95": -162256,            "high_rebalance_count": 2,
        }

    deriv_portfolio = load_csv_safe("module 4/module4_portfolio.csv")

    st.markdown("""
    <style>
    .section-label {
        font-size: 13px; font-weight: 800; letter-spacing: 1.2px;
        color: #6b7280; text-transform: uppercase; margin-bottom: 10px;
    }
    .dashboard-header {
        background: #f3f4f6; padding: 26px 28px;
        border-radius: 0px; margin-bottom: 22px;
    }
    .dashboard-title    { font-size: 28px; font-weight: 800; color: #111827; margin-bottom: 4px; }
    .dashboard-subtitle { font-size: 16px; color: #6b7280; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">Derivatives Risk Dashboard</div>
        <div class="dashboard-subtitle">
            NIFTY Options &nbsp;·&nbsp; 2 Feb 2024 &nbsp;·&nbsp;
            Near-Term ATM Portfolio &nbsp;·&nbsp;
            {:,} option records &nbsp;·&nbsp; {:} strikes &nbsp;·&nbsp; {:} expiries
        </div>
    </div>
    """.format(dm["dataset_size"], dm["strikes_count"], dm["expiries_count"]),
    unsafe_allow_html=True)

    # ── KPI row: exposure + VaR ──────────────────────────────────────
    st.markdown('<div class="section-label">Portfolio Risk Exposure</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Portfolio Delta",       f"{dm['port_delta']:,.1f}",        "Net directional exposure")
    k2.metric("Portfolio Gamma",       f"{dm['port_gamma']:.2f}",          "Long γ — benefits high vol")
    k3.metric("VaR (95%)",             f"₹{abs(dm['var_95']):,.0f}",       "Max expected daily loss")
    k4.metric("VaR (99%)",             f"₹{abs(dm['var_99']):,.0f}",       "Tail risk threshold")
    k5.metric("CVaR (95%)",            f"₹{abs(dm['cvar_95']):,.0f}",      "Avg loss past VaR breach")
    k6.metric("High-Urgency Contracts",dm.get("high_rebalance_count", "—"),"Needs 5-min rebalancing")

    st.divider()

    # ── Risk dashboard chart ─────────────────────────────────────────
    # Contains: P&L curve, VaR histogram, IV surface, delta exposure, theta decay
    st.markdown('<div class="section-label">Risk Visualisation</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.caption(
            "P&L under ±5% spot shock · VaR / CVaR distribution · "
            "Implied volatility surface · Delta exposure by contract · Theta decay"
        )
        _rd = Path("module 4/risk_dashboard.png")
        if _rd.exists():
            st.image(str(_rd), use_container_width=True)
        else:
            st.warning("Re-run the derivatives notebook to generate risk_dashboard.png")

    st.divider()

    # ── Hedging action ───────────────────────────────────────────────
    st.markdown('<div class="section-label">Delta-Neutral Hedging Action</div>', unsafe_allow_html=True)

    sig_l, sig_r = st.columns([1, 2])

    with sig_l:
        with st.container(border=True):
            st.subheader("Hedge Signals")
            _delta_dir = "Short" if dm["port_delta"] < 0 else "Long"
            st.metric(
                "Delta Neutralisation",
                f"{_delta_dir} {abs(int(dm['port_delta'])):,} NIFTY units",
                "To flatten net delta"
            )
            _hedge_cost_cr = abs(dm["port_delta"]) * dm["nifty_spot"] / 1e7
            st.metric("Estimated Hedge Cost", f"₹{_hedge_cost_cr:.2f} Cr")
            st.metric(
                "ML Pricing Edge",
                f"₹{dm['best_rmse']:.2f} RMSE",
                f"{dm['bs_improvement_pct']:.1f}% better than Black-Scholes"
            )
            st.caption(
                "Portfolio is long gamma (+{:.2f}). "
                "Rebalance HIGH-urgency contracts at every 5-min bar.".format(dm["port_gamma"])
            )

    with sig_r:
        with st.container(border=True):
            st.subheader("Portfolio Contract Details")
            if not deriv_portfolio.empty:
                if "Hedge_Cost_INR" in deriv_portfolio.columns:
                    deriv_portfolio["Hedge_Cost_INR"] = deriv_portfolio["Hedge_Cost_INR"].apply(
                        lambda x: f"₹{float(x):,.0f}" if pd.notna(x) else "—"
                    )
                # Colour-code urgency for readability
                display_cols = [c for c in [
                    "Strike", "Option_Type", "Delta", "Gamma", "Vega", "Theta",
                    "Hedge_Action", "Hedge_Cost_INR", "Rebalance_Urgency"
                ] if c in deriv_portfolio.columns]
                st.dataframe(deriv_portfolio[display_cols], hide_index=True, use_container_width=True)
            else:
                st.info("Run notebook to generate outputs/module4_portfolio.csv")