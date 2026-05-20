from pathlib import Path
import math
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

GRID_RISK_PATH = ROOT / "data/features/grid_risk_scores_202503.parquet"
POLE_BASE_PATH = ROOT / "data/interim/pole_base.parquet"

GRID_SUMMARY_PATH = ROOT / "data/features/grid_risk_summary_202503.parquet"
POLE_RISK_PATH = ROOT / "data/features/pole_risk_scores_202503.parquet"

OUT_DIR = ROOT / "data/outputs"
CANDIDATE_DIR = OUT_DIR / "submission_candidates"
TOP_POLES_PATH = OUT_DIR / "top_risk_poles_1000.csv"
REPORT_PATH = ROOT / "reports/pole_risk_submission_report.md"

SUBMISSION_COLUMNS = ["pole_id", "lon", "lat", "decision"]


def require_columns(df: pd.DataFrame, required: list[str], name: str):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing columns: {missing}\nActual columns: {list(df.columns)}")


def build_grid_risk_summary(grid_risk: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        grid_risk,
        [
            "grid_id",
            "date",
            "pole_count",
            "center_lon",
            "center_lat",
            "grid_risk_score",
            "grid_risk_score_100",
            "dry_weather_score",
            "wind_score",
            "asset_exposure_score",
            "warning_score",
        ],
        "grid_risk",
    )

    df = grid_risk.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["grid_risk_score"] = pd.to_numeric(df["grid_risk_score"], errors="coerce")
    df["grid_risk_score_100"] = pd.to_numeric(df["grid_risk_score_100"], errors="coerce")

    idx = df.groupby("grid_id")["grid_risk_score"].idxmax()
    peak = df.loc[idx, [
        "grid_id",
        "date",
        "grid_risk_score",
        "grid_risk_score_100",
        "dry_weather_score",
        "wind_score",
        "asset_exposure_score",
        "warning_score",
        "primary_temp_max",
        "primary_humidity_min",
        "primary_rain_sum",
        "rain_sum_7d",
        "primary_wind_max",
        "wind_max_7d",
        "no_rain_days",
        "dry_warning_flag",
        "strong_wind_warning_flag",
    ]].copy()

    peak = peak.rename(columns={
        "date": "peak_date",
        "grid_risk_score": "peak_grid_risk_score",
        "grid_risk_score_100": "peak_grid_risk_score_100",
        "dry_weather_score": "peak_dry_weather_score",
        "wind_score": "peak_wind_score",
        "asset_exposure_score": "peak_asset_exposure_score",
        "warning_score": "peak_warning_score",
        "primary_temp_max": "peak_temp_max",
        "primary_humidity_min": "peak_humidity_min",
        "primary_rain_sum": "peak_rain_sum",
        "rain_sum_7d": "peak_rain_sum_7d",
        "primary_wind_max": "peak_wind_max",
        "wind_max_7d": "peak_wind_max_7d",
        "no_rain_days": "peak_no_rain_days",
        "dry_warning_flag": "peak_dry_warning_flag",
        "strong_wind_warning_flag": "peak_strong_wind_warning_flag",
    })

    summary = (
        df.groupby("grid_id", as_index=False)
        .agg(
            pole_count=("pole_count", "first"),
            pole_density=("pole_density", "first"),
            center_lon=("center_lon", "first"),
            center_lat=("center_lat", "first"),
            risk_mean=("grid_risk_score", "mean"),
            risk_max=("grid_risk_score", "max"),
            risk_p95=("grid_risk_score", lambda x: x.quantile(0.95)),
            risk_p90=("grid_risk_score", lambda x: x.quantile(0.90)),
            risk_std=("grid_risk_score", "std"),
            date_count=("date", "nunique"),
            high_day_count=("grid_risk_score", lambda x: int((x >= 0.60).sum())),
            very_high_day_count=("grid_risk_score", lambda x: int((x >= 0.70).sum())),
            dry_weather_mean=("dry_weather_score", "mean"),
            wind_mean=("wind_score", "mean"),
            asset_exposure_mean=("asset_exposure_score", "mean"),
            warning_mean=("warning_score", "mean"),
        )
    )

    summary["risk_std"] = summary["risk_std"].fillna(0)
    summary["high_day_ratio"] = summary["high_day_count"] / summary["date_count"].replace(0, np.nan)
    summary["very_high_day_ratio"] = summary["very_high_day_count"] / summary["date_count"].replace(0, np.nan)

    # 최종 grid-level risk: 한 달 동안의 평균보다 peak/p95를 더 중시
    summary["grid_final_risk_score"] = (
        0.35 * summary["risk_max"]
        + 0.35 * summary["risk_p95"]
        + 0.20 * summary["risk_mean"]
        + 0.10 * summary["high_day_ratio"].fillna(0)
    ).clip(0, 1)

    summary["grid_final_risk_score_100"] = (summary["grid_final_risk_score"] * 100).round(3)

    summary = summary.merge(peak, on="grid_id", how="left")

    summary["grid_final_risk_grade"] = pd.cut(
        summary["grid_final_risk_score"],
        bins=[-0.001, 0.20, 0.40, 0.60, 0.80, 1.001],
        labels=["very_low", "low", "medium", "high", "very_high"],
    ).astype(str)

    return summary.sort_values("grid_final_risk_score", ascending=False).reset_index(drop=True)


def build_pole_risk(pole_base: pd.DataFrame, grid_summary: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        pole_base,
        ["pole_id", "lon", "lat", "grid_id"],
        "pole_base",
    )

    keep_grid_cols = [
        "grid_id",
        "pole_count",
        "pole_density",
        "grid_final_risk_score",
        "grid_final_risk_score_100",
        "grid_final_risk_grade",
        "risk_mean",
        "risk_max",
        "risk_p95",
        "risk_p90",
        "high_day_count",
        "very_high_day_count",
        "high_day_ratio",
        "peak_date",
        "peak_grid_risk_score_100",
        "peak_dry_weather_score",
        "peak_wind_score",
        "peak_asset_exposure_score",
        "peak_warning_score",
        "peak_temp_max",
        "peak_humidity_min",
        "peak_rain_sum",
        "peak_rain_sum_7d",
        "peak_wind_max",
        "peak_wind_max_7d",
        "peak_no_rain_days",
        "peak_dry_warning_flag",
        "peak_strong_wind_warning_flag",
    ]

    existing = [c for c in keep_grid_cols if c in grid_summary.columns]
    out = pole_base.merge(grid_summary[existing], on="grid_id", how="left")

    out["pole_risk_score"] = out["grid_final_risk_score"]
    out["pole_risk_score_100"] = out["grid_final_risk_score_100"]

    out = out.sort_values(
        ["pole_risk_score", "pole_count", "pole_id"],
        ascending=[False, False, True],
    ).reset_index(drop=True)

    out["pole_risk_rank"] = np.arange(1, len(out) + 1)
    out["pole_risk_percentile"] = out["pole_risk_rank"] / len(out)

    return out


def make_submission(pole_risk: pd.DataFrame, top_pct: float, path: Path) -> dict:
    n = len(pole_risk)
    cutoff_n = max(1, math.ceil(n * top_pct))

    sub = pole_risk[["pole_id", "lon", "lat"]].copy()
    sub["decision"] = 0

    high_idx = pole_risk.index[:cutoff_n]
    sub.loc[high_idx, "decision"] = 1

    sub = sub[SUBMISSION_COLUMNS]
    path.parent.mkdir(parents=True, exist_ok=True)
    sub.to_csv(path, index=False, encoding="utf-8-sig")

    return {
        "file": str(path.relative_to(ROOT)),
        "top_pct": top_pct,
        "decision_1_count": int(sub["decision"].sum()),
        "decision_0_count": int((sub["decision"] == 0).sum()),
        "rows": len(sub),
    }


def main():
    if not GRID_RISK_PATH.exists():
        raise FileNotFoundError(f"Missing grid risk file: {GRID_RISK_PATH}")

    if not POLE_BASE_PATH.exists():
        raise FileNotFoundError(f"Missing pole base file: {POLE_BASE_PATH}")

    grid_risk = pd.read_parquet(GRID_RISK_PATH)
    pole_base = pd.read_parquet(POLE_BASE_PATH)

    print("grid_risk:", grid_risk.shape)
    print("pole_base:", pole_base.shape)

    grid_summary = build_grid_risk_summary(grid_risk)
    pole_risk = build_pole_risk(pole_base, grid_summary)

    GRID_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    POLE_RISK_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    grid_summary.to_parquet(GRID_SUMMARY_PATH, index=False)
    pole_risk.to_parquet(POLE_RISK_PATH, index=False)

    top_poles = pole_risk.head(1000).copy()
    top_poles.to_csv(TOP_POLES_PATH, index=False, encoding="utf-8-sig")

    candidate_specs = [
        ("baseline_submission_top1.csv", 0.01),
        ("baseline_submission_top3.csv", 0.03),
        ("baseline_submission_top5.csv", 0.05),
        ("baseline_submission_top10.csv", 0.10),
    ]

    candidate_rows = []
    for filename, pct in candidate_specs:
        candidate_rows.append(
            make_submission(
                pole_risk,
                top_pct=pct,
                path=CANDIDATE_DIR / filename,
            )
        )

    candidate_df = pd.DataFrame(candidate_rows)

    grid_score_summary = grid_summary[
        [
            "grid_final_risk_score_100",
            "risk_mean",
            "risk_max",
            "risk_p95",
            "high_day_count",
            "pole_count",
        ]
    ].describe(percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).reset_index()

    pole_score_summary = pole_risk[
        [
            "pole_risk_score_100",
            "pole_count",
            "risk_max",
            "risk_p95",
            "high_day_count",
        ]
    ].describe(percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).reset_index()

    grade_summary = (
        pole_risk.groupby("grid_final_risk_grade", as_index=False)
        .agg(
            pole_count=("pole_id", "count"),
            grid_count=("grid_id", "nunique"),
            mean_score=("pole_risk_score_100", "mean"),
            max_score=("pole_risk_score_100", "max"),
        )
        .sort_values("max_score", ascending=False)
    )

    top_grid_summary = grid_summary.head(30)[
        [
            "grid_id",
            "pole_count",
            "center_lon",
            "center_lat",
            "grid_final_risk_score_100",
            "grid_final_risk_grade",
            "risk_max",
            "risk_p95",
            "high_day_count",
            "peak_date",
            "peak_grid_risk_score_100",
            "peak_temp_max",
            "peak_humidity_min",
            "peak_wind_max",
            "peak_no_rain_days",
        ]
    ]

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Pole Risk Submission Report\n\n")

        f.write("## 1. Input Summary\n\n")
        f.write(f"- grid_risk_rows: {len(grid_risk)}\n")
        f.write(f"- grid_count: {grid_risk['grid_id'].nunique()}\n")
        f.write(f"- date_count: {grid_risk['date'].nunique()}\n")
        f.write(f"- pole_base_rows: {len(pole_base)}\n\n")

        f.write("## 2. Output Files\n\n")
        f.write(f"- grid_summary: {GRID_SUMMARY_PATH}\n")
        f.write(f"- pole_risk: {POLE_RISK_PATH}\n")
        f.write(f"- top_risk_poles_1000: {TOP_POLES_PATH}\n\n")

        f.write("## 3. Grid Final Risk Formula\n\n")
        f.write("`	ext\n")
        f.write("grid_final_risk_score = 0.35 * risk_max\n")
        f.write("                      + 0.35 * risk_p95\n")
        f.write("                      + 0.20 * risk_mean\n")
        f.write("                      + 0.10 * high_day_ratio\n")
        f.write("`\n\n")

        f.write("## 4. Candidate Submission Files\n\n")
        f.write(candidate_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 5. Grid Score Summary\n\n")
        f.write(grid_score_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 6. Pole Score Summary\n\n")
        f.write(pole_score_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 7. Grade Summary\n\n")
        f.write(grade_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 8. Top 30 Risk Grids\n\n")
        f.write(top_grid_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 9. Notes\n\n")
        f.write("- This is a rule-based baseline submission generator.\n")
        f.write("- Final official submission should be selected after threshold sensitivity review.\n")
        f.write("- Since no public label is available, top-percentile submissions are generated as candidates.\n")

    print("Saved:", GRID_SUMMARY_PATH)
    print("Saved:", POLE_RISK_PATH)
    print("Saved:", TOP_POLES_PATH)
    print("Saved:", REPORT_PATH)
    print()
    print(candidate_df)
    print()
    print(pole_risk.head())


if __name__ == "__main__":
    main()
