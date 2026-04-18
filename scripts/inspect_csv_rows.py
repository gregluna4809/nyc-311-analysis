import sys
import pandas as pd

def main(path: str, start_row: int, nrows: int):
    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        skiprows=range(1, start_row),
        nrows=nrows,
    )
    print(df.to_string(index=False))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts\\inspect_csv_rows.py <csv_path> <start_row> <nrows>")
        sys.exit(1)

    csv_path = sys.argv[1]
    start_row = int(sys.argv[2])
    nrows = int(sys.argv[3])

    main(csv_path, start_row, nrows)