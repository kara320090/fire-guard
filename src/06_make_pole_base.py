from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

IN_PATH = ROOT / "data" / "interim" / "poles_5179.parquet"
OUT_PATH = ROOT / "data" / "interim" / "pole_base.parquet"
REPORT_PATH = ROOT / "reports" / "pole_base_report.md"

REQUIRED_COLUMNS = [
    "pole_id",
    "lon",
    "lat",
    "x_5179",
    "y_5179",
    "grid_ix",
    "grid_iy",
    "grid_id",
]

def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {IN_PATH}")

    df = pd.read_parquet(IN_PATH)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    base = df[REQUIRED_COLUMNS].copy()

    before = len(base)
    base = base.dropna(subset=["pole_id", "lon", "lat", "grid_id"]).copy()
    base = base.drop_duplicates(subset=["pole_id"], keep="first").copy()
    after = len(base)

    base.to_parquet(OUT_PATH, index=False)

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Pole Base Report\n\n")
        f.write("## Purpose\n\n")
        f.write("pole_base.parquet is the canonical pole-level table for FIRE-GUARD submission and feature joining.\n\n")
        f.write("## Summary\n\n")
        f.write(f"- input_file: {IN_PATH}\n")
        f.write(f"- output_file: {OUT_PATH}\n")
        f.write(f"- input_rows: {before}\n")
        f.write(f"- output_rows: {after}\n")
        f.write(f"- duplicated_pole_id_after_clean: {int(base['pole_id'].duplicated().sum())}\n")
        f.write(f"- missing_lon: {int(base['lon'].isna().sum())}\n")
        f.write(f"- missing_lat: {int(base['lat'].isna().sum())}\n")
        f.write(f"- unique_grid_count: {base['grid_id'].nunique()}\n\n")
        f.write("## Columns\n\n")
        for col in base.columns:
            f.write(f"- {col}\n")

    print("Saved:", OUT_PATH)
    print("Report:", REPORT_PATH)
    print("Shape:", base.shape)
    print(base.head())

if __name__ == "__main__":
    main()
