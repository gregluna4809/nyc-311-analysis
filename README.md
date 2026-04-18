# NYC 311 Service Requests Analysis (Q1 2024)

[![Live Demo](https://img.shields.io/badge/Live_Demo-Open_Dashboard-success?style=for-the-badge&logo=streamlit)](https://nyc311-analysis-gregluna.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Postgres](https://img.shields.io/badge/Postgres-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/cloud)

> **Live dashboard:** [nyc311-analysis-gregluna.streamlit.app](https://nyc311-analysis-gregluna.streamlit.app/)

An end-to-end data pipeline and interactive dashboard analyzing **794,226 NYC 311 service requests** from Q1 2024. The project spans API ingestion, PostgreSQL storage, SQL analysis, visualization, and cloud deployment — a complete workflow from raw public data to a live, publicly accessible dashboard.

---

## Key Findings

- **Brooklyn led total complaint volume** in every month of Q1 2024.
- **The Bronx was disproportionately housing-driven** — HEAT/HOT WATER alone accounted for **24.13%** of its complaints.
- **Manhattan skewed toward dense-urban issues**: noise (multiple subcategories), vendor and street activity, and for-hire vehicle complaints.
- **Staten Island over-indexed on infrastructure**: street condition, sewer, and water system complaints (3.5–3.8x the citywide baseline).
- **Agency response times varied widely** — EDC's median closure time sat around 15 days, while NYPD and DOHMH resolved requests in under a day.

---

## Architecture

```
 ┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
 │ NYC Open Data    │     │ PostgreSQL      │     │ Streamlit        │
 │ (Socrata API)    │────▶│ (Docker local   │────▶│ Dashboard        │
 │                  │     │  / Supabase     │     │ (Plotly charts)  │
 │ ~800k rows       │     │  production)    │     │                  │
 └──────────────────┘     └─────────────────┘     └──────────────────┘
         │                        ▲                        │
         │                        │                        │
         │               Same schema, same indexes         │
         │                                                 │
         ▼                                                 ▼
    scripts/load_from_api.py                      Streamlit Community
    (paginated ingestion,                             Cloud (hosted)
     50k rows per batch)
```

The app reads a single `DATABASE_URL` environment variable so the same code runs against local Docker for development and Supabase for production, with no code changes.

---

## Tech Stack

| Layer            | Tool                         |
| ---------------- | ---------------------------- |
| Ingestion        | Python, Socrata API          |
| Storage (dev)    | PostgreSQL 16 in Docker      |
| Storage (prod)   | Supabase (managed Postgres)  |
| Analysis         | SQL (window functions, CTEs) |
| Dashboard        | Streamlit + Plotly           |
| Deployment       | Streamlit Community Cloud    |
| Version control  | Git / GitHub                 |

---

## Data Source

NYC Open Data — 311 Service Requests ([data.cityofnewyork.us](https://data.cityofnewyork.us/))

- Pulled via the public Socrata API (`erm2-nwe9`)
- Filtered to Q1 2024 (Jan 1 – Mar 31)
- Final dataset: 794,226 rows

---

## Pipeline

### 1. Ingestion
- Paginated API requests at 50,000 rows per batch
- Authenticated with an app token for improved throughput
- Landed raw data into a staging area for cleaning

### 2. Cleaning
- Type-converted timestamps and numeric fields
- Normalized missing values (`NaN` → `NULL`)
- Standardized schema across ingestion batches

### 3. Database
- Table: `service_requests`
- Indexes on `created_date`, `borough`, and `complaint_type` for query performance
- Same schema mirrored between local Docker and Supabase

### 4. Analysis (SQL)
SQL queries stored in `/sql/analysis/`:
- Monthly complaint volume by borough
- Top 10 complaint types per borough (window function ranking)
- HEAT/HOT WATER share analysis
- Borough anomaly detection (overrepresentation ratios vs. citywide baseline)
- Median response time by agency (cleaned: valid closures under 30 days)

### 5. Visualization
- Streamlit dashboard with interactive borough filtering
- Plotly bar and dataframe visualizations
- KPI metrics, comparative charts, and anomaly table

---

## Project Structure

```
nyc-311-analysis/
│
├── app.py                      # Streamlit dashboard (reads DATABASE_URL)
├── docker-compose.yml          # Local PostgreSQL container
├── requirements.txt
├── .env                        # Local credentials (gitignored)
│
├── scripts/
│   ├── load_from_api.py        # API ingestion
│   ├── download_data.py
│   ├── load_data.py
│   └── profile_csv.py
│
├── sql/
│   ├── schema.sql
│   └── analysis/
│       ├── 01_volume_by_borough_month.sql
│       ├── 02_top_10_complaint_types_by_borough.sql
│       ├── 04_heat_complaint_share_by_borough.sql
│       ├── 05_borough_anomaly_detection.sql
│       └── 06_median_response_time_by_agency_clean.sql
│
└── data/
    └── raw/
```

---

## Running Locally

### 1. Start the database

```bash
docker compose up -d
```

### 2. Set up environment

Create a `.env` file at the project root:

```
DATABASE_URL=postgresql://nyc311_user:nyc311_password@localhost:5434/nyc311
SOCRATA_APP_TOKEN=your_token_here
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Load data

```bash
python scripts/load_from_api.py --start-date 2024-01-01 --end-date 2024-03-31
```

### 5. Launch the dashboard

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## Deployment

The live dashboard is deployed via **Streamlit Community Cloud**, connected directly to this GitHub repository. The production database is a managed **Supabase** Postgres instance. Database credentials are stored as Streamlit secrets, never in the repo.

Migration from local Docker to Supabase was done with `pg_dump` + `psql` — table, data, and indexes all transferred cleanly.

---

## What This Project Demonstrates

- End-to-end data pipeline design — from public API to live dashboard
- Cloud-native deployment (managed Postgres + PaaS hosting)
- SQL-driven analytical thinking (window functions, CTEs, percentile aggregations)
- Environment-aware application design (single codebase, multiple deployment targets)
- Data cleaning, schema design, and indexing for query performance
- Translating raw data into actionable insight

---

## Future Improvements

- Time-series trend decomposition
- Normalize complaint volume by borough population
- Geospatial visualization using complaint lat/lon
- Automated daily ingestion with scheduled jobs
- Additional quarters of data for year-over-year comparisons

---

## Author

**Gregory Luna**
LinkedIn: [linkedin.com/in/gregvluna](https://www.linkedin.com/in/gregvluna)
GitHub: [github.com/gregluna4809](https://github.com/gregluna4809)

---

*This project reflects a shift from intuition-based observation to data-driven analysis — combining domain awareness with structured querying, cloud infrastructure, and interactive visualization.*
