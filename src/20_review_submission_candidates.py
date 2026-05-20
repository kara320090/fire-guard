from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_DIR = ROOT / "data/outputs/submission_candidates"
POLE_RISK_PATH = ROOT / "data/features/pole_risk_scores_202503.parquet"

FINAL_OUT = ROOT / "data/outputs/baseline_submission_final_top5.csv"
REPORT_PATH = ROOT / "reports/submission_candidate_review.md"

CANDIDATES = {
    "top1": CANDIDATE_DIR / "baseline_submission_top1.csv",
    "top3": CANDIDATE_DIR / "baseline_submission_top3.csv",
    "top5": CANDIDATE_DIR / "baseline_submission_top5.csv",
    "top10": CANDIDATE_DIR / "baseline_submission_top10.csv",
}

REQUIRED_COLUMNS = ["pole_id", "lon", "lat", "decision"]


def validate_submission(path: Path) -> dict:
    if not path.exists():
        return {
            "candidate": path.stem,
            "file": str(path.relative_to(ROOT)),
            "exists": False,
            "rows": None,
            "columns_ok": False,
            "decision_values": "",
            "decision_1_count": None,
            "decision_1_ratio": None,
            "lon_missing": None,
            "lat_missing": None,
            "pole_id_duplicate": None,
        }

    df = pd.read_csv(path, encoding="utf-8-sig")

    columns_ok = list(df.columns) == REQUIRED_COLUMNS
    decision_values = sorted(df["decision"].dropna().unique().tolist()) if "decision" in df.columns else []

    return {
        "candidate": path.stem,
        "file": str(path.relative_to(ROOT)),
        "exists": True,
        "rows": len(df),
        "columns_ok": columns_ok,
        "decision_values": str(decision_values),
        "decision_1_count": int(df["decision"].sum()) if "decision" in df.columns else None,
        "decision_1_ratio": float(df["decision"].mean()) if "decision" in df.columns else None,
        "lon_missing": int(df["lon"].isna().sum()) if "lon" in df.columns else None,
        "lat_missing": int(df["lat"].isna().sum()) if "lat" in df.columns else None,
        "pole_id_duplicate": int(df["pole_id"].duplicated().sum()) if "pole_id" in df.columns else None,
    }


def main():
    rows = []

    for name, path in CANDIDATES.items():
        item = validate_submission(path)
        item["name"] = name
        rows.append(item)

    review = pd.DataFrame(rows)

    if not CANDIDATES["top5"].exists():
        raise FileNotFoundError(f"Missing top5 candidate: {CANDIDATES['top5']}")

    top5 = pd.read_csv(CANDIDATES["top5"], encoding="utf-8-sig")
    FINAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    top5.to_csv(FINAL_OUT, index=False, encoding="utf-8-sig")

    pole_risk = pd.read_parquet(POLE_RISK_PATH)

    high_poles = pole_risk.head(20)[[
        "pole_id",
        "lon",
        "lat",
        "grid_id",
        "pole_risk_score_100",
        "grid_final_risk_grade",
        "risk_max",
        "risk_p95",
        "high_day_count",
        "peak_date",
        "peak_temp_max",
        "peak_humidity_min",
        "peak_wind_max",
        "peak_no_rain_days",
    ]]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Submission Candidate Review\n\n")

        f.write("## 1. Candidate Validation\n\n")
        f.write(review.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 2. Selected Baseline\n\n")
        f.write("- selected_file: data/outputs/baseline_submission_final_top5.csv\n")
        f.write("- reason: top5 is selected as the default rule-based baseline because it balances conservative detection and sufficient high-risk coverage without labels.\n\n")

        f.write("## 3. Top 20 Risk Poles\n\n")
        f.write(high_poles.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 4. Notes\n\n")
        f.write("- top1 is a conservative candidate.\n")
        f.write("- top3 is a backup conservative baseline.\n")
        f.write("- top5 is the default baseline candidate.\n")
        f.write("- top10 may be too broad without validation labels.\n")

    print("Saved:", FINAL_OUT)
    print("Saved:", REPORT_PATH)
    print(review)


if __name__ == "__main__":
    main()
