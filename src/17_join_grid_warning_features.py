from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

GRID_FEATURE_PATH = ROOT / "data/features/grid_day_features_202503.parquet"
WARNING_DAILY_PATH = ROOT / "data/interim/warning_daily_202503.parquet"

OUT_PATH = ROOT / "data/features/grid_day_features_with_warning_202503.parquet"
REPORT_PATH = ROOT / "reports/grid_warning_features_report.md"


WARNING_COLUMNS = [
    "dry_warning_flag",
    "strong_wind_warning_flag",
    "dry_and_windy_warning_flag",
    "dry_warning_count",
    "strong_wind_warning_count",
    "dry_warning_level_max",
    "strong_wind_level_max",
    "warning_event_count",
]


def main():
    if not GRID_FEATURE_PATH.exists():
        raise FileNotFoundError(f"Missing grid feature file: {GRID_FEATURE_PATH}")

    if not WARNING_DAILY_PATH.exists():
        raise FileNotFoundError(
            f"Missing warning daily file: {WARNING_DAILY_PATH}\n"
            "먼저 python src\\16_make_warning_daily.py 를 실행하세요."
        )

    grid = pd.read_parquet(GRID_FEATURE_PATH)
    warning = pd.read_parquet(WARNING_DAILY_PATH)

    if "date" not in grid.columns:
        raise ValueError("grid feature file missing date column")

    if "date" not in warning.columns:
        raise ValueError("warning daily file missing date column")

    grid["date"] = pd.to_datetime(grid["date"], errors="coerce")
    warning["date"] = pd.to_datetime(warning["date"], errors="coerce")

    keep_warning_cols = ["date"] + [c for c in WARNING_COLUMNS if c in warning.columns]

    if len(keep_warning_cols) == 1:
        raise ValueError(f"No warning columns found. Actual columns: {list(warning.columns)}")

    warning_keep = warning[keep_warning_cols].copy()

    out = grid.merge(warning_keep, on="date", how="left")

    for c in WARNING_COLUMNS:
        if c in out.columns:
            out[c] = out[c].fillna(0).astype(int)

    # risk scoring 직전용 기본 상호작용 feature
    if "primary_humidity_deficit" in out.columns and "dry_warning_flag" in out.columns:
        out["dryness_warning_interaction"] = (
            out["primary_humidity_deficit"] * out["dry_warning_flag"]
        )

    if "primary_wind_max" in out.columns and "strong_wind_warning_flag" in out.columns:
        out["wind_warning_interaction"] = (
            out["primary_wind_max"] * out["strong_wind_warning_flag"]
        )

    if "dry_and_windy_warning_flag" in out.columns:
        out["warning_risk_boost"] = (
            out["dry_warning_flag"] * 1.0
            + out["strong_wind_warning_flag"] * 1.0
            + out["dry_and_windy_warning_flag"] * 1.5
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    out.to_parquet(OUT_PATH, index=False)

    summary = {
        "grid_input_rows": len(grid),
        "warning_rows": len(warning),
        "output_rows": len(out),
        "grid_count": out["grid_id"].nunique() if "grid_id" in out.columns else None,
        "date_count": out["date"].nunique(),
        "date_min": out["date"].min(),
        "date_max": out["date"].max(),
    }

    warning_summary_cols = [c for c in WARNING_COLUMNS if c in out.columns]
    warning_summary = out[warning_summary_cols].sum().reset_index()
    warning_summary.columns = ["feature", "sum"]

    date_warning_summary = (
        out.groupby("date", as_index=False)
        .agg(
            rows=("date", "count"),
            dry_warning_rows=("dry_warning_flag", "sum") if "dry_warning_flag" in out.columns else ("date", "count"),
            strong_wind_warning_rows=("strong_wind_warning_flag", "sum") if "strong_wind_warning_flag" in out.columns else ("date", "count"),
            dry_and_windy_warning_rows=("dry_and_windy_warning_flag", "sum") if "dry_and_windy_warning_flag" in out.columns else ("date", "count"),
        )
        .sort_values("date")
    )

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Grid Warning Features Report\n\n")

        f.write("## 1. Summary\n\n")
        for k, v in summary.items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## 2. Warning Feature Sum\n\n")
        f.write(warning_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 3. Date Warning Coverage\n\n")
        f.write(date_warning_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 4. Output Columns\n\n")
        for c in out.columns:
            f.write(f"- {c}\n")

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print(summary)
    print(warning_summary)


if __name__ == "__main__":
    main()
