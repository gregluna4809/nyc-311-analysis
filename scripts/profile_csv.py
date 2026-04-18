import sys
import pandas as pd

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

SUSPECT_BOROUGHS = {
    "BROOKLYN", "BRONX", "MANHATTAN", "QUEENS", "STATEN ISLAND", "Unspecified"
}

def main(path: str):
    print(f"Profiling: {path}\n")

    df = pd.read_csv(path, dtype=str, keep_default_na=False, nrows=200000)

    print("Columns found:")
    print(df.columns.tolist())
    print()

    print("Row count sampled:")
    print(len(df))
    print()

    print("Null/blank-like counts:")
    for col in df.columns:
        blanks = (df[col].astype(str).str.strip() == "").sum()
        print(f"{col}: {blanks}")
    print()

    print("Max string lengths:")
    for col in df.columns:
        max_len = df[col].astype(str).map(len).max()
        print(f"{col}: {max_len}")
    print()

    if all(col in df.columns for col in EXPECTED_COLUMNS):
        suspect_rows = df[
            df["incident_zip"].isin(SUSPECT_BOROUGHS)
            | df["status"].isin(SUSPECT_BOROUGHS)
            | df["incident_zip"].eq("In Progress")
            | df["incident_zip"].eq("Closed")
        ][EXPECTED_COLUMNS]

        print("Sample suspicious rows:")
        print(suspect_rows.head(20).to_string(index=False))
        print()
    else:
        print("Expected columns do not fully match this file.")
        print("That means the file itself may be malformed or from an older download.")
        print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts\\profile_csv.py <csv_path>")
        sys.exit(1)

    main(sys.argv[1])