import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from outputs.dashboard import load_data

st.set_page_config(
    page_title="Executive Project Portfolio Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================
# @st.cache_data

# def load_data(uploaded_file):
#     df = pd.read_csv(uploaded_file)
#     return df

# st.title("📊 Executive Portfolio Investment Dashboard")
# st.markdown("AI-Assisted Capital Allocation & Portfolio Review Dashboard")

# uploaded_file = st.sidebar.file_uploader(
#     "Upload Project Portfolio CSV",
#     type=["csv"]
# )

# if uploaded_file is None:
#     st.info("Please upload your project portfolio CSV file to continue.")
#     st.stop()

# =====================================================
# DATA PREPARATION
# =====================================================
uploaded_file = pd.read_csv('../outputs/op_1.csv')

df = load_data(uploaded_file)

numeric_cols = [
    'Predicted_NPV',
    'Predicted_Success_Probability',
    'Financial_Strength',
    'Feasibility_Score',
    'Final_Score',
    'ROI_Index',
    'Risk_Adjusted_Return',
    'Composite_Score',
    'Expected_Value',
    'NPV'
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# # =====================================================
# # EXECUTIVE VALIDATION LOGIC
# # =====================================================

# def classify_financial_profile(row):

#     # Strong Strategic Fund
#     if (
#         row['Recommendation'] == 'Fund' and
#         row['Financial_Strength'] >= 0.55 and
#         row['Feasibility_Score'] >= 0.45 and
#         row['Predicted_NPV'] > 1000000 and
#         row['ROI_Index'] > 1
#     ):
#         return 'Strategic Fund'

#     # Aggressive Growth Fund
#     elif (
#         row['Recommendation'] in ['Fund', 'Review'] and
#         row['Predicted_NPV'] > 1000000 and
#         row['ROI_Index'] > 0.30 and
#         row['Predicted_Success_Probability'] >= 0.30 and
#         row['Financial_Strength'] >= 0.40
#     ):
#         return 'Aggressive Growth'

#     # Balanced Review
#     elif (
#         row['Recommendation'] == 'Review' and
#         row['Financial_Strength'] >= 0.35 and
#         row['Feasibility_Score'] >= 0.35
#     ):
#         return 'Balanced Review'

#     # Risk Concern Review
#     elif (
#         row['Recommendation'] == 'Review' and
#         row['Financial_Strength'] < 0.35
#     ):
#         return 'Risk Concern'

#     # Weak Reject
#     elif (
#         row['Recommendation'] == 'Reject' and
#         (
#             row['NPV'] < 0 or
#             row['ROI_Index'] < 0 or
#             row['Financial_Strength'] < 0.30
#         )
#     ):
#         return 'Financially Weak'

#     # Borderline Opportunity
#     elif (
#         row['Recommendation'] == 'Reject' and
#         row['Predicted_NPV'] > 0 and
#         row['Predicted_Success_Probability'] >= 0.30
#     ):
#         return 'Borderline Opportunity'

#     return 'Needs Executive Review'


# def calculate_priority_score(row):
#     score = (
#         (row['Financial_Strength'] * 30) +
#         (row['Feasibility_Score'] * 25) +
#         (row['Predicted_Success_Probability'] * 20) +
#         (min(row['ROI_Index'], 5) / 5 * 15) +
#         (max(min(row['Predicted_NPV'] / 3000000, 1), 0) * 10)
#     )

#     return round(score, 2)


# # Apply classification

# df['Executive_Category'] = df.apply(classify_financial_profile, axis=1)
# df['Executive_Priority_Score'] = df.apply(calculate_priority_score, axis=1)

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Dashboard Filters")

recommendation_filter = st.sidebar.multiselect(
    "Recommendation",
    options=sorted(df['Recommendation'].unique()),
    default=sorted(df['Recommendation'].unique())
)

category_filter = st.sidebar.multiselect(
    "Executive Category",
    options=sorted(df['Executive_Category'].unique()),
    default=sorted(df['Executive_Category'].unique())
)

department_filter = st.sidebar.multiselect(
    "Department",
    options=sorted(df['Department'].unique()),
    default=sorted(df['Department'].unique())
)

filtered_df = df[
    (df['Recommendation'].isin(recommendation_filter)) &
    (df['Executive_Category'].isin(category_filter)) &
    (df['Department'].isin(department_filter))
]

# =====================================================
# KPI SECTION
# =====================================================

st.subheader("📌 Portfolio Executive Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Projects",
        len(filtered_df)
    )

with col2:
    funded_count = len(filtered_df[filtered_df['Recommendation'] == 'Fund'])
    st.metric(
        "Projects to Fund",
        funded_count
    )

with col3:
    review_count = len(filtered_df[filtered_df['Recommendation'] == 'Review'])
    st.metric(
        "Projects to Review",
        review_count
    )

with col4:
    total_npv = filtered_df['Predicted_NPV'].sum()
    st.metric(
        "Portfolio Predicted NPV",
        f"${total_npv:,.0f}"
    )

with col5:
    avg_success = filtered_df['Predicted_Success_Probability'].mean()
    st.metric(
        "Avg Success Probability",
        f"{avg_success:.1%}"
    )

# =====================================================
# EXECUTIVE INSIGHTS
# =====================================================

# st.subheader("🎯 Why Projects Were Selected")

# insight_col1, insight_col2 = st.columns(2)

# with insight_col1:
#     fig = px.scatter(
#         filtered_df,
#         x='Financial_Strength',
#         y='Feasibility_Score',
#         color='Recommendation',
#         size='Predicted_NPV',
#         hover_data=['Project_ID', 'Department'],
#         title='Financial Strength vs Feasibility',
#         height=500
#     )

#     fig.add_hline(y=0.35, line_dash='dash')
#     fig.add_vline(x=0.35, line_dash='dash')

#     st.plotly_chart(fig, use_container_width=True)

# with insight_col2:
#     fig2 = px.scatter(
#         filtered_df,
#         x='ROI_Index',
#         y='Predicted_Success_Probability',
#         color='Executive_Category',
#         size='Expected_Value',
#         hover_data=['Project_ID'],
#         title='ROI vs Success Probability',
#         height=500
#     )

#     st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# PORTFOLIO DISTRIBUTION
# =====================================================

st.subheader("📈 Portfolio Allocation Analysis")

portfolio_col1, portfolio_col2 = st.columns(2)

with portfolio_col1:

    rec_summary = (
        filtered_df.groupby('Recommendation')
        .size()
        .reset_index(name='Projects')
    )

    pie_fig = px.pie(
        rec_summary,
        names='Recommendation',
        values='Projects',
        title='Recommendation Distribution'
    )

    st.plotly_chart(pie_fig, use_container_width=True)

with portfolio_col2:

    dept_summary = (
        filtered_df.groupby(['Department', 'Recommendation'])
        .size()
        .reset_index(name='Projects')
    )

    dept_fig = px.sunburst(
        dept_summary,
        path=['Department', 'Recommendation'],
        values='Projects',
        title='Department-Level Funding Mix'
    )

    st.plotly_chart(dept_fig, use_container_width=True)

# =====================================================
# DEPARTMENT FUNDING ANALYSIS
# =====================================================

st.subheader("🏢 Department Investment Analysis")

investment_summary = (
    filtered_df.groupby('Department')
    .agg({
        'Investment_Cost': 'sum',
        'Predicted_NPV': 'sum',
        'Project_ID': 'count'
    })
    .reset_index()
)

investment_summary.columns = [
    'Department',
    'Total_Investment',
    'Total_Predicted_NPV',
    'Project_Count'
]

bar_fig = px.bar(
    investment_summary,
    x='Department',
    y='Total_Predicted_NPV',
    color='Project_Count',
    title='Department Portfolio Value Contribution',
    text_auto=True,
    height=500
)

st.plotly_chart(bar_fig, use_container_width=True)

# =====================================================
# TOP PROJECTS SECTION
# =====================================================

st.subheader("🏆 Top Recommended Projects")

ranking_df = filtered_df.sort_values(
    by='Executive_Priority_Score',
    ascending=False
)

show_top = st.slider(
    "Select Top Projects",
    min_value=5,
    max_value=min(30, len(ranking_df)),
    value=10
)

priority_view = ranking_df.head(show_top)

heatmap_df = priority_view[[
    'Project_ID',
    'Financial_Strength',
    'Feasibility_Score',
    'Predicted_Success_Probability',
    'ROI_Index',
    'Final_Score'
]]

heatmap_fig = px.imshow(
    heatmap_df.set_index('Project_ID'),
    aspect='auto',
    title='Top Project Score Heatmap'
)

st.plotly_chart(heatmap_fig, use_container_width=True)

# =====================================================
# EXECUTIVE DECISION TABLE
# =====================================================

st.subheader("📋 Executive Decision Table")

final_cols = [
    'Project_ID',
    'Department',
    'Recommendation',
    'Executive_Category',
    'Executive_Priority_Score',
    'Predicted_NPV',
    'Predicted_Success_Probability',
    'Financial_Strength',
    'Feasibility_Score',
    'ROI_Index',
    'Risk_Score',
    'Final_Score',
    'Review_Priority'
]

final_table = ranking_df[final_cols]

st.dataframe(
    final_table,
    use_container_width=True,
    height=600
)

# =====================================================
# DOWNLOAD SECTION
# =====================================================

csv = final_table.to_csv(index=False).encode('utf-8')

st.download_button(
    label="⬇ Download Executive Portfolio Report",
    data=csv,
    file_name='executive_project_portfolio_analysis.csv',
    mime='text/csv'
)

# =====================================================
# EXECUTIVE COMMENTARY
# =====================================================

st.subheader("🧠 Executive Portfolio Interpretation")

funded = filtered_df[filtered_df['Recommendation'] == 'Fund']
review = filtered_df[filtered_df['Recommendation'] == 'Review']
reject = filtered_df[filtered_df['Recommendation'] == 'Reject']

st.markdown(f'''
### Key Observations

- **{len(funded)} projects** demonstrate strong investment viability with healthy financial strength and positive expected return characteristics.

- **{len(review)} projects** require strategic or leadership review due to moderate feasibility, elevated uncertainty, or dependency on execution quality.

- **{len(reject)} projects** currently show weak economic justification, low risk-adjusted return, or negative long-term value contribution.

### Financial Interpretation Logic

The recommendation framework combines:

1. Predicted NPV
2. ROI Quality
3. Financial Strength
4. Feasibility Score
5. Success Probability
6. Risk Adjusted Return
7. Composite ML Scoring

### Executive Guidance

- Fund projects with sustainable positive NPV and strong operational feasibility.
- Review projects with upside potential but execution or financial uncertainty.
- Reject projects where capital efficiency and long-term value remain weak.
''')

st.success("Dashboard generated successfully.")
