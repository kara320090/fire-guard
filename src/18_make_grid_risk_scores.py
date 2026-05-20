from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data/features/grid_day_features_with_warning_202503.parquet"
OUT_PATH = ROOT / "data/features/grid_risk_scores_202503.parquet"
REPORT_PATH = ROOT / "reports/grid_risk_scores_report.md"


def robust_minmax(s: pd.Series, q_low=0.01, q_high=0.99) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")

    if x.notna().sum() == 0:
        return pd.Series(0.0, index=s.index)

    lo = x.quantile(q_low)
    hi = x.quantile(q_high)

    if pd.isna(lo) or pd.isna(hi) or hi <= lo:
        return pd.Series(0.0, index=s.index)

    clipped = x.clip(lo, hi)
    return ((clipped - lo) / (hi - lo)).fillna(0.0)


def require_columns(df: pd.DataFrame, cols: list[str]):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def add_score_components(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    require_columns(
        out,
        [
            "grid_id",
            "date",
            "pole_count",
            "primary_humidity_min",
            "primary_humidity_deficit",
            "primary_temp_max",
            "primary_wind_max",
            "rain_sum_7d",
            "wind_max_7d",
            "humidity_min_7d",
            "no_rain_days",
            "primary_station_distance_km",
        ],
    )

    # warning columns may exist after 17_join_grid_warning_features.py
    for c in [
        "dry_warning_flag",
        "strong_wind_warning_flag",
        "dry_and_windy_warning_flag",
        "dry_warning_count",
        "strong_wind_warning_count",
        "dry_warning_level_max",
        "strong_wind_level_max",
        "warning_event_count",
    ]:
        if c not in out.columns:
            out[c] = 0

    out["date"] = pd.to_datetime(out["date"], errors="coerce")

    # 1. 건조 위험
    humidity_deficit_norm = robust_minmax(out["primary_humidity_deficit"])
    no_rain_norm = robust_minmax(out["no_rain_days"])
    temp_norm = robust_minmax(out["primary_temp_max"])

    # 최근 7일 강수량이 낮을수록 위험
    rain7_norm = robust_minmax(out["rain_sum_7d"])
    rain_deficit_norm = 1.0 - rain7_norm

    # 최근 7일 최저습도가 낮을수록 위험
    humidity_min7_norm = robust_minmax(out["humidity_min_7d"])
    low_humidity7_norm = 1.0 - humidity_min7_norm

    out["dry_weather_score"] = (
        0.30 * humidity_deficit_norm
        + 0.25 * no_rain_norm
        + 0.20 * rain_deficit_norm
        + 0.15 * low_humidity7_norm
        + 0.10 * temp_norm
    )

    # 2. 강풍 위험
    wind_now_norm = robust_minmax(out["primary_wind_max"])
    wind7_norm = robust_minmax(out["wind_max_7d"])

    out["wind_score"] = (
        0.55 * wind_now_norm
        + 0.45 * wind7_norm
    )

    # 3. 전력설비 노출도
    out["asset_exposure_score"] = robust_minmax(np.log1p(out["pole_count"]))

    # 4. 특보 위험
    dry_warning = pd.to_numeric(out["dry_warning_flag"], errors="coerce").fillna(0)
    wind_warning = pd.to_numeric(out["strong_wind_warning_flag"], errors="coerce").fillna(0)
    both_warning = pd.to_numeric(out["dry_and_windy_warning_flag"], errors="coerce").fillna(0)

    dry_level = robust_minmax(out["dry_warning_level_max"])
    wind_level = robust_minmax(out["strong_wind_level_max"])
    event_count = robust_minmax(out["warning_event_count"])

    out["warning_score"] = (
        0.25 * dry_warning
        + 0.25 * wind_warning
        + 0.20 * both_warning
        + 0.15 * dry_level
        + 0.10 * wind_level
        + 0.05 * event_count
    ).clip(0, 1)

    # 5. 관측소 거리 불확실성: 위험점수 본체에는 직접 크게 반영하지 않고, 설명/검수용으로 둠
    out["distance_uncertainty_score"] = robust_minmax(out["primary_station_distance_km"])

    # 최종 grid risk score
    out["grid_risk_score"] = (
        0.40 * out["dry_weather_score"]
        + 0.25 * out["wind_score"]
        + 0.20 * out["asset_exposure_score"]
        + 0.15 * out["warning_score"]
    ).clip(0, 1)

    out["grid_risk_score_100"] = (out["grid_risk_score"] * 100).round(3)

    # 등급은 보고서/지도용. 제출 decision은 다음 단계에서 별도 threshold로 결정.
    out["grid_risk_grade"] = pd.cut(
        out["grid_risk_score"],
        bins=[-0.001, 0.20, 0.40, 0.60, 0.80, 1.001],
        labels=["very_low", "low", "medium", "high", "very_high"],
    ).astype(str)

    return out


def make_report(df: pd.DataFrame):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    score_cols = [
        "dry_weather_score",
        "wind_score",
        "asset_exposure_score",
        "warning_score",
        "distance_uncertainty_score",
        "grid_risk_score",
        "grid_risk_score_100",
    ]

    score_summary = df[score_cols].describe(
        percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    ).reset_index()

    grade_summary = (
        df.groupby("grid_risk_grade", as_index=False)
        .agg(
            rows=("grid_id", "count"),
            grid_count=("grid_id", "nunique"),
            mean_score=("grid_risk_score_100", "mean"),
            max_score=("grid_risk_score_100", "max"),
        )
        .sort_values("max_score", ascending=False)
    )

    date_summary = (
        df.groupby("date", as_index=False)
        .agg(
            rows=("grid_id", "count"),
            mean_risk=("grid_risk_score_100", "mean"),
            max_risk=("grid_risk_score_100", "max"),
            high_grid_count=("grid_risk_score", lambda x: int((x >= 0.60).sum())),
            very_high_grid_count=("grid_risk_score", lambda x: int((x >= 0.80).sum())),
            dry_warning_days=("dry_warning_flag", "max"),
            strong_wind_warning_days=("strong_wind_warning_flag", "max"),
        )
        .sort_values("date")
    )

    top_grids = (
        df.sort_values("grid_risk_score", ascending=False)
        .head(50)
        [[
            "date",
            "grid_id",
            "pole_count",
            "center_lon",
            "center_lat",
            "primary_weather_source",
            "primary_temp_max",
            "primary_humidity_min",
            "primary_rain_sum",
            "rain_sum_7d",
            "primary_wind_max",
            "wind_max_7d",
            "no_rain_days",
            "dry_warning_flag",
            "strong_wind_warning_flag",
            "grid_risk_score_100",
            "grid_risk_grade",
        ]]
    )

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Grid Risk Scores Report\n\n")

        f.write("## 1. Output Summary\n\n")
        f.write(f"- output: {OUT_PATH}\n")
        f.write(f"- rows: {len(df)}\n")
        f.write(f"- grid_count: {df['grid_id'].nunique()}\n")
        f.write(f"- date_count: {df['date'].nunique()}\n")
        f.write(f"- date_min: {df['date'].min()}\n")
        f.write(f"- date_max: {df['date'].max()}\n\n")

        f.write("## 2. Risk Formula\n\n")
        f.write("`	ext\n")
        f.write("grid_risk_score = 0.40 * dry_weather_score\n")
        f.write("                + 0.25 * wind_score\n")
        f.write("                + 0.20 * asset_exposure_score\n")
        f.write("                + 0.15 * warning_score\n")
        f.write("`\n\n")

        f.write("## 3. Score Summary\n\n")
        f.write(score_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 4. Grade Summary\n\n")
        f.write(grade_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 5. Date Summary\n\n")
        f.write(date_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 6. Top 50 Risk Grid-Day Rows\n\n")
        f.write(top_grids.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 7. Output Columns\n\n")
        for c in df.columns:
            f.write(f"- {c}\n")


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Missing input file: {INPUT_PATH}\n"
            "먼저 python src\\17_join_grid_warning_features.py 를 실행하세요."
        )

    df = pd.read_parquet(INPUT_PATH)
    print("Input:", df.shape)

    scored = add_score_components(df)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    scored.to_parquet(OUT_PATH, index=False)

    make_report(scored)

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print(scored[[
        "grid_id",
        "date",
        "grid_risk_score_100",
        "grid_risk_grade",
        "dry_weather_score",
        "wind_score",
        "asset_exposure_score",
        "warning_score",
    ]].head())


if __name__ == "__main__":
    main()
