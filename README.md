# NYC 311 Service Requests Analysis (Q1 2024)

An end-to-end data pipeline and interactive dashboard analyzing New York City's 311 service requests from January through March 2024.

The goal was to move past raw complaint counts and surface meaningful patterns in how service requests are distributed, composed, and resolved across the five boroughs. The project spans ingestion, cleaning, database modeling, SQL analysis, and visualization in a single reproducible workflow.

---

## Key Findings

- **Brooklyn led total complaint volume** in every month of Q1 2024.
- **The Bronx was disproportionately housing-driven** — HEAT/HOT WATER alone accounted for over **24%** of its complaints.
- **Manhattan skewed toward dense-urban issues**: noise (multiple subcategories), vendor and street activity, and for-hire vehicle complaints.
- **Staten Island over-indexed on infrastructure**: street condition, sewer, and water system complaints.
- **Agency response times varied widely** — some agencies closed requests within hours, others took multiple days.

---

## Tech Stack

- **Python** — ingestion, cleaning, dashboard
- **PostgreSQL** — storage and querying
- **Docker** — containerized database
- **SQL** — analysis layer
- **Streamlit** — interactive dashboard
- **Plotly** — visualizations

---

## Data Source

NYC Open Data — 311 Service Requests
[https://data.cityofnewyork.us/](https://data.cityofnewyork.us/)

- Pulled via the public API endpoint
- Filtered to Q1 2024 (Jan 1 – Mar 31)

---

## Pipeline Architecture

### 1. Data Ingestion
- Pulled from the NYC Open Data API in Python
- Paginated requests at 50,000 rows per batch
- Authenticated with an API token for higher throughput

### 2. Data Cleaning
- Type-converted timestamps and numeric fields
- Normalized missing values (NaN → NULL)
- Standardized schema across ingestion batches

### 3. Database Layer
- PostgreSQL running in Docker
- Table: `service_requests`
- Indexes on `created_date`, `borough`, and `complaint_type`

### 4. Analysis Layer (SQL)
- Monthly complaint volume by borough
- Top complaint types per borough
- Heat-complaint share analysis
- Borough anomaly detection
- Median response time by agency

### 5. Visualization Layer
- Streamlit dashboard with interactive filtering
- Plotly charts for all visualizations

---

## Project Structure

```
nyc-311-analysis/
│
├── app.py                      # Streamlit dashboard
├── docker-compose.yml          # PostgreSQL container
├── requirements.txt
├── .env                        # database + API credentials
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

## How to Run

### 1. Start the database

```bash
docker compose up -d
```

### 2. Activate the virtual environment

```bash
.\.venv\Scripts\Activate
```

### 3. Load data from the API

```bash
python scripts/load_from_api.py --start-date 2024-01-01 --end-date 2024-03-31
```

### 4. Launch the dashboard

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Screenshots

*(Add screenshots of the dashboard here)*

---

## What This Project Demonstrates

- End-to-end data pipeline design
- Working with large public datasets at scale
- SQL-driven analytical thinking
- Data cleaning and schema design
- Building interactive dashboards
- Translating raw data into actionable insight

---

## Future Improvements

- Time-series trend analysis
- Normalize complaint volume by borough population
- Geospatial visualization (maps)
- Deploy dashboard to the cloud (Streamlit Cloud or AWS)
- Automated daily ingestion

---

## Author

**Gregory Luna**
LinkedIn: [linkedin.com/in/gregvluna](https://www.linkedin.com/in/gregvluna)
GitHub: [github.com/gregluna4809](https://github.com/gregluna4809)

---

*This project reflects a shift from intuition-based observation to data-driven analysis — combining domain awareness with structured querying and interactive visualization.*
