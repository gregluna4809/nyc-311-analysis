import os
import pandas as pd
import streamlit as st
import plotly.express as px
import psycopg2
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="NYC 311 Q1 2024 Dashboard",
    layout="wide"
)

st.title("NYC 311 Service Requests Dashboard")
st.subheader("Q1 2024 | AI-assisted pipeline + SQL analysis")
st.markdown(
    """
**Key finding:** The Bronx had the highest concentration of housing-related complaints,
with HEAT/HOT WATER accounting for over 24% of all service requests.
"""
)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

@st.cache_data(show_spinner=False)
def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()

summary_query = """
SELECT
    COUNT(*) AS total_requests,
    COUNT(DISTINCT borough) AS borough_count,
    MIN(created_date) AS min_date,
    MAX(created_date) AS max_date
FROM service_requests;
"""

borough_month_query = """
SELECT
    DATE_TRUNC('month', created_date)::date AS month,
    borough,
    COUNT(*) AS complaint_count
FROM service_requests
WHERE created_date IS NOT NULL
  AND borough IS NOT NULL
  AND borough <> ''
GROUP BY 1, 2
ORDER BY 1, 3 DESC;
"""

top_complaints_query = """
WITH ranked_complaints AS (
    SELECT
        borough,
        complaint_type,
        COUNT(*) AS complaint_count,
        ROW_NUMBER() OVER (
            PARTITION BY borough
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM service_requests
    WHERE borough IS NOT NULL
      AND borough <> ''
      AND borough <> 'Unspecified'
      AND complaint_type IS NOT NULL
      AND complaint_type <> ''
    GROUP BY borough, complaint_type
)
SELECT
    borough,
    complaint_type,
    complaint_count
FROM ranked_complaints
WHERE rn <= 10
ORDER BY borough, complaint_count DESC;
"""

heat_share_query = """
WITH totals AS (
  SELECT borough, COUNT(*) AS total
  FROM service_requests
  WHERE borough NOT IN ('', 'Unspecified')
  GROUP BY borough
),
heat AS (
  SELECT borough, COUNT(*) AS heat_cnt
  FROM service_requests
  WHERE borough NOT IN ('', 'Unspecified')
    AND complaint_type = 'HEAT/HOT WATER'
  GROUP BY borough
)
SELECT
  t.borough,
  heat_cnt,
  total,
  ROUND(heat_cnt::numeric / total * 100, 2) AS pct_heat
FROM totals t
JOIN heat h USING (borough)
ORDER BY pct_heat DESC;
"""

response_time_query = """
SELECT
    agency,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY (EXTRACT(EPOCH FROM (closed_date - created_date)) / 3600) / 24
        )::numeric,
        2
    ) AS median_response_days
FROM service_requests
WHERE created_date IS NOT NULL
  AND closed_date IS NOT NULL
  AND closed_date >= created_date
  AND (closed_date - created_date) < INTERVAL '30 days'
GROUP BY agency
ORDER BY median_response_days DESC;
"""

anomaly_query = """
WITH borough_totals AS (
    SELECT borough, COUNT(*) AS borough_total
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
    GROUP BY borough
),
city_totals AS (
    SELECT COUNT(*) AS city_total
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
),
complaint_counts AS (
    SELECT borough, complaint_type, COUNT(*) AS cnt
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
    GROUP BY borough, complaint_type
),
city_complaints AS (
    SELECT complaint_type, COUNT(*) AS city_cnt
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
    GROUP BY complaint_type
)
SELECT
    c.borough,
    c.complaint_type,
    ROUND(c.cnt::numeric / b.borough_total * 100, 2) AS borough_pct,
    ROUND(cc.city_cnt::numeric / ct.city_total * 100, 2) AS city_pct,
    ROUND(
        (c.cnt::numeric / b.borough_total) /
        (cc.city_cnt::numeric / ct.city_total),
        2
    ) AS overrepresentation_ratio
FROM complaint_counts c
JOIN borough_totals b ON c.borough = b.borough
JOIN city_complaints cc ON c.complaint_type = cc.complaint_type
JOIN city_totals ct ON true
WHERE c.cnt > 500
ORDER BY overrepresentation_ratio DESC
LIMIT 25;
"""

summary_df = run_query(summary_query)
borough_month_df = run_query(borough_month_query)
top_complaints_df = run_query(top_complaints_query)
heat_share_df = run_query(heat_share_query)
response_time_df = run_query(response_time_query)
anomaly_df = run_query(anomaly_query)

summary_row = summary_df.iloc[0]

anomaly_df["borough_pct"] = anomaly_df["borough_pct"].round(2)
anomaly_df["city_pct"] = anomaly_df["city_pct"].round(2)
anomaly_df["overrepresentation_ratio"] = anomaly_df["overrepresentation_ratio"].round(2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", f"{int(summary_row['total_requests']):,}")
col2.metric("Boroughs Present", f"{int(summary_row['borough_count'])}")
col3.metric("Start Date", str(summary_row["min_date"])[:10])
col4.metric("End Date", str(summary_row["max_date"])[:10])

st.divider()

st.header("Complaint Volume by Borough and Month")
borough_options = sorted([b for b in borough_month_df["borough"].dropna().unique()])
selected_boroughs = st.multiselect(
    "Select boroughs",
    borough_options,
    default=[b for b in borough_options if b != "Unspecified"]
)

filtered_borough_month = borough_month_df[
    borough_month_df["borough"].isin(selected_boroughs)
].copy()

fig_volume = px.bar(
    filtered_borough_month,
    x="month",
    y="complaint_count",
    color="borough",
    barmode="group",
    title="311 Complaint Volume by Borough and Month"
)
fig_volume.update_layout(
    xaxis_title="Month",
    yaxis_title="Complaint Count",
    legend_title="Borough",
    bargap=0.2
)
st.plotly_chart(fig_volume, use_container_width=True)

st.divider()

left_col, right_col = st.columns(2)

with left_col:
    st.header("Top Complaint Types by Borough")
    borough_choice = st.selectbox(
        "Choose a borough",
        sorted([b for b in top_complaints_df["borough"].unique()])
    )

    filtered_top = top_complaints_df[top_complaints_df["borough"] == borough_choice].copy()

    fig_top = px.bar(
        filtered_top,
        x="complaint_count",
        y="complaint_type",
        orientation="h",
        title=f"Top 10 Complaint Types in {borough_choice}"
    )
    fig_top.update_layout(
        xaxis_title="Complaint Count",
        yaxis_title="Complaint Type",
        yaxis={"categoryorder": "total ascending"}
    )
    st.plotly_chart(fig_top, use_container_width=True)

with right_col:
    st.header("Heat / Hot Water Complaint Share")
    fig_heat = px.bar(
        heat_share_df,
        x="borough",
        y="pct_heat",
        title="HEAT/HOT WATER as Share of Borough Complaints (%)",
        text="pct_heat"
    )
    fig_heat.update_layout(
        xaxis_title="Borough",
        yaxis_title="Percent of Complaints"
    )
    fig_heat.update_traces(textposition="outside")
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

left_col, right_col = st.columns(2)

with left_col:
    st.header("Median Response Time by Agency")
    response_time_sorted = response_time_df.sort_values(
        "median_response_days",
        ascending=False
    ).copy()

    fig_response = px.bar(
        response_time_sorted,
        x="agency",
        y="median_response_days",
        title="Median Response Time by Agency (Days)"
    )
    fig_response.update_layout(
        xaxis_title="Agency",
        yaxis_title="Median Response Days"
    )
    st.plotly_chart(fig_response, use_container_width=True)

with right_col:
    st.header("Overrepresented Complaint Types by Borough")
    st.caption("Complaint types overrepresented relative to the city-wide baseline")
    st.dataframe(anomaly_df, use_container_width=True, hide_index=True)

st.divider()

st.header("Key Takeaways")
st.markdown(
    """
- Brooklyn had the highest total 311 complaint volume in each month of Q1 2024.
- The Bronx had the highest concentration of HEAT/HOT WATER complaints.
- Manhattan showed strong overrepresentation in dense urban complaint categories such as noise, vendors, and for-hire vehicle issues.
- Staten Island stood out for infrastructure-heavy complaint types such as street condition, sewer, and water system.
- Median response times varied significantly by agency.
"""
)