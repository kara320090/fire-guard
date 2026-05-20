from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

POLE_BASE_PATH = ROOT / "data" / "interim" / "pole_base.parquet"
OUT_DIR = ROOT / "data" / "outputs"
REPORT_PATH = ROOT / "reports" / "submission_template_report.md"

TEMPLATE_PATH = OUT_DIR / "submission_template.csv"
BASELINE_PATH = OUT_DIR / "baseline_submission_all_zero.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

SUBMISSION_COLUMNS = ["pole_id", "lon", "lat", "decision"]

def main():
    if not POLE_BASE_PATH.exists():
        raise FileNotFoundError(f"Missing pole base file: {POLE_BASE_PATH}")

    pole = pd.read_parquet(POLE_BASE_PATH)

    required = ["pole_id", "lon", "lat"]
    missing = [c for c in required if c not in pole.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    sub = pole[["pole_id", "lon", "lat"]].copy()
    sub["decision"] = 0
    sub = sub[SUBMISSION_COLUMNS]

    sub.to_csv(TEMPLATE_PATH, index=False, encoding="utf-8-sig")
    sub.to_csv(BASELINE_PATH, index=False, encoding="utf-8-sig")

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Submission Template Report\n\n")
        f.write("## Purpose\n\n")
        f.write("Create official submission-format CSV files with pole_id, lon, lat, decision.\n\n")
        f.write("## Output\n\n")
        f.write(f"- template: {TEMPLATE_PATH}\n")
        f.write(f"- baseline_all_zero: {BASELINE_PATH}\n")
        f.write(f"- rows: {len(sub)}\n")
        f.write(f"- columns: {list(sub.columns)}\n")
        f.write(f"- decision_unique_values: {sorted(sub['decision'].unique().tolist())}\n")

    print("Saved:", TEMPLATE_PATH)
    print("Saved:", BASELINE_PATH)
    print("Rows:", len(sub))
    print(sub.head())

if __name__ == "__main__":
    main()
