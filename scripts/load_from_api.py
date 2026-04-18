import os
import requests
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from time import sleep

load_dotenv()

BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

COLUMNS = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "complaint_type",
    "descriptor",
    "location_type",
    "borough",
    "incident_zip",
    "status",
    "latitude",
    "longitude"
]


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def fetch_batch(start, end, offset, limit=50000):
    params = {
        "$select": ",".join(COLUMNS),
        "$where": f"created_date between '{start}T00:00:00' and '{end}T23:59:59'",
        "$limit": limit,
        "$offset": offset,
        "$order": "created_date ASC"
    }

    r = requests.get(BASE_URL, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def clean(df):
    df = pd.DataFrame(df)
    df = df.reindex(columns=COLUMNS)

    df["unique_key"] = pd.to_numeric(df["unique_key"], errors="coerce")
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df["closed_date"] = pd.to_datetime(df["closed_date"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Convert pandas missing values (NaN/NaT) to real Python None
    df = df.astype(object)
    df = df.where(pd.notna(df), None)

    return df


def insert_batch(conn, df):
    cur = conn.cursor()

    rows = [tuple(x) for x in df.to_numpy()]

    cur.executemany("""
        INSERT INTO service_requests (
            unique_key,
            created_date,
            closed_date,
            agency,
            complaint_type,
            descriptor,
            location_type,
            borough,
            incident_zip,
            status,
            latitude,
            longitude
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (unique_key) DO NOTHING
    """, rows)

    conn.commit()
    cur.close()


def load_range(start, end):
    conn = get_conn()

    offset = 0
    total = 0

    while True:
        print(f"Fetching offset {offset}...")

        data = fetch_batch(start, end, offset)

        if not data:
            break

        df = clean(data)
        insert_batch(conn, df)

        total += len(df)
        print(f"Inserted {len(df):,} | total {total:,}")

        offset += 50000
        sleep(0.2)

    conn.close()
    print(f"Done: {total:,} rows")


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load NYC 311 data directly from API into Postgres.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    load_range(args.start_date, args.end_date)