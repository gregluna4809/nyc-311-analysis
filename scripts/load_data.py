import os
import sys
from io import StringIO

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

TABLE_NAME = "service_requests"
CHUNK_SIZE = 100_000

EXPECTED_COLUMNS = [
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
    "longitude",
]


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def clean_chunk(df: pd.DataFrame) -> pd.DataFrame:
    # Keep only the columns we expect, in the right order
    df = df[EXPECTED_COLUMNS].copy()

    # Normalize blanks
    df = df.where(pd.notna(df), None)

    # Parse timestamps
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df["closed_date"] = pd.to_datetime(df["closed_date"], errors="coerce")

    # Numeric conversions
    df["unique_key"] = pd.to_numeric(df["unique_key"], errors="coerce").astype("Int64")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Convert pandas NaT/NA back to None for PostgreSQL COPY
    df = df.where(pd.notna(df), None)

    return df


def copy_chunk(cur, df: pd.DataFrame):
    from io import StringIO

    try:
        buffer = StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        cur.copy_expert(
            f"""
            COPY service_requests (
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
            FROM STDIN
            WITH (
                FORMAT CSV,
                NULL ''
            )
            """,
            buffer,
        )

    except Exception as e:
        print("⚠️ Chunk failed, falling back to row-by-row insert")

        # fallback: insert rows one at a time
        for _, row in df.iterrows():
            try:
                cur.execute(
                    """
                    INSERT INTO service_requests VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (unique_key) DO NOTHING
                    """,
                    tuple(row),
                )
            except Exception:
                # skip bad row
                continue


def load_csv(csv_path: str):
    conn = get_connection()
    cur = conn.cursor()

    total_rows = 0

    try:
        for i, chunk in enumerate(
            pd.read_csv(
                csv_path,
                chunksize=CHUNK_SIZE,
                dtype=str,
                keep_default_na=False,
            ),
            start=1,
        ):
            cleaned = clean_chunk(chunk)
            copy_chunk(cur, cleaned)
            conn.commit()

            total_rows += len(cleaned)
            print(f"Loaded chunk {i}: {len(cleaned):,} rows | total: {total_rows:,}")

        print(f"Finished loading {csv_path}")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts\\load_data.py <csv_path>")
        sys.exit(1)

    load_csv(sys.argv[1])