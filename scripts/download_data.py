import argparse
import os
import time
import requests
import pandas as pd

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

DEFAULT_BATCH_SIZE = 50000


def fetch_batch(start_date: str, end_date: str, offset: int, limit: int) -> list[dict]:
    params = {
        "$select": ",".join(COLUMNS),
        "$where": (
            f"created_date between '{start_date}T00:00:00' "
            f"and '{end_date}T23:59:59'"
        ),
        "$order": "created_date ASC",
        "$limit": limit,
        "$offset": offset
    }

    response = requests.get(BASE_URL, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Download NYC 311 data in batches.")
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Rows per batch")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    offset = 0
    total_rows = 0
    first_write = True

    while True:
        print(f"Fetching rows {offset} to {offset + args.batch_size - 1}...")

        data = fetch_batch(
            start_date=args.start_date,
            end_date=args.end_date,
            offset=offset,
            limit=args.batch_size
        )

        if not data:
            print("No more data returned.")
            break

        df = pd.DataFrame(data)

        # Force every batch into the exact same schema and order
        df = df.reindex(columns=COLUMNS)

        df.to_csv(
            args.output,
            mode="w" if first_write else "a",
            header=first_write,
            index=False
        )

        batch_count = len(df)
        total_rows += batch_count
        print(f"Wrote {batch_count:,} rows. Total so far: {total_rows:,}")

        first_write = False
        offset += args.batch_size

        time.sleep(0.25)

    print(f"Done. Saved {total_rows:,} rows to {args.output}")


if __name__ == "__main__":
    main()