from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

GRID_STATION_PATH = ROOT / "data/interim/grid_station_mapping_202503.parquet"
WEATHER_DAILY_PATH = ROOT / "data/interim/weather_daily_202503.parquet"

OUT_PATH = ROOT / "data/features/grid_day_features_202503.parquet"
REPORT_PATH = ROOT / "reports/grid_day_features_report.md"


WEATHER_VALUE_COLUMNS = [
    "temp_mean",
    "temp_max",
    "temp_min",
    "humidity_mean",
    "humidity_min",
    "rain_sum",
    "wind_mean",
    "wind_max",
    "wind_dir_mean",
    "pressure_mean",
    "row_count",
    "temp_obs_count",
    "humidity_obs_count",
    "wind_obs_count",
    "rain_obs_count",
]


def load_inputs():
    if not GRID_STATION_PATH.exists():
        raise FileNotFoundError(f"Missing grid-station mapping: {GRID_STATION_PATH}")

    if not WEATHER_DAILY_PATH.exists():
        raise FileNotFoundError(f"Missing weather daily: {WEATHER_DAILY_PATH}")

    grid = pd.read_parquet(GRID_STATION_PATH)
    weather = pd.read_parquet(WEATHER_DAILY_PATH)

    grid_required = [
        "grid_id",
        "pole_count",
        "pole_density",
        "center_lon",
        "center_lat",
        "nearest_aws_station_id",
        "nearest_aws_distance_m",
        "nearest_asos_station_id",
        "nearest_asos_distance_m",
    ]

    weather_required = [
        "station_id",
        "station_name",
        "date",
        "source_type",
    ]

    grid_missing = [c for c in grid_required if c not in grid.columns]
    weather_missing = [c for c in weather_required if c not in weather.columns]

    if grid_missing:
        raise ValueError(f"Grid mapping missing columns: {grid_missing}")

    if weather_missing:
        raise ValueError(f"Weather daily missing columns: {weather_missing}")

    grid["nearest_aws_station_id"] = pd.to_numeric(
        grid["nearest_aws_station_id"], errors="coerce"
    ).astype("Int64")
    grid["nearest_asos_station_id"] = pd.to_numeric(
        grid["nearest_asos_station_id"], errors="coerce"
    ).astype("Int64")

    weather["station_id"] = pd.to_numeric(weather["station_id"], errors="coerce").astype("Int64")
    weather["date"] = pd.to_datetime(weather["date"], errors="coerce")
    weather["source_type"] = weather["source_type"].astype(str).str.lower()

    return grid, weather


def make_grid_date_base(grid: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    dates = (
        weather["date"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    if len(dates) == 0:
        raise RuntimeError("No valid dates found in weather_daily.")

    date_df = pd.DataFrame({"date": dates})
    date_df["__key"] = 1

    base = grid.copy()
    base["__key"] = 1

    out = base.merge(date_df, on="__key", how="inner").drop(columns=["__key"])

    return out


def prepare_weather_for_merge(weather: pd.DataFrame, source_type: str, prefix: str) -> pd.DataFrame:
    src = weather[weather["source_type"] == source_type].copy()

    available_cols = [c for c in WEATHER_VALUE_COLUMNS if c in src.columns]

    keep_cols = ["station_id", "date"] + available_cols

    src = src[keep_cols].copy()

    rename = {
        "station_id": f"nearest_{prefix}_station_id",
    }

    for c in available_cols:
        rename[c] = f"{prefix}_{c}"

    src = src.rename(columns=rename)

    return src


def attach_weather(base: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    aws = prepare_weather_for_merge(weather, "aws", "aws")
    asos = prepare_weather_for_merge(weather, "asos", "asos")

    out = base.merge(
        aws,
        on=["nearest_aws_station_id", "date"],
        how="left",
    )

    out = out.merge(
        asos,
        on=["nearest_asos_station_id", "date"],
        how="left",
    )

    return out


def add_primary_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # AWS가 있으면 AWS를 우선 사용, 없으면 ASOS를 backup으로 사용
    out["has_aws_weather"] = out.get("aws_row_count").notna()
    out["has_asos_weather"] = out.get("asos_row_count").notna()

    out["primary_weather_source"] = np.select(
        [
            out["has_aws_weather"],
            ~out["has_aws_weather"] & out["has_asos_weather"],
        ],
        [
            "aws",
            "asos",
        ],
        default="missing",
    )

    source_cols = [
        "temp_mean",
        "temp_max",
        "temp_min",
        "humidity_mean",
        "humidity_min",
        "rain_sum",
        "wind_mean",
        "wind_max",
        "wind_dir_mean",
        "pressure_mean",
    ]

    for c in source_cols:
        aws_col = f"aws_{c}"
        asos_col = f"asos_{c}"

        if aws_col in out.columns and asos_col in out.columns:
            out[f"primary_{c}"] = out[aws_col].combine_first(out[asos_col])
        elif aws_col in out.columns:
            out[f"primary_{c}"] = out[aws_col]
        elif asos_col in out.columns:
            out[f"primary_{c}"] = out[asos_col]
        else:
            out[f"primary_{c}"] = np.nan

    out["primary_station_distance_m"] = np.where(
        out["primary_weather_source"] == "aws",
        out["nearest_aws_distance_m"],
        np.where(
            out["primary_weather_source"] == "asos",
            out["nearest_asos_distance_m"],
            np.nan,
        ),
    )

    out["primary_station_distance_km"] = out["primary_station_distance_m"] / 1000.0

    # 건조 관련 기본 파생변수
    out["primary_humidity_deficit"] = 100 - out["primary_humidity_min"]

    return out


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values(["grid_id", "date"]).copy()

    group = out.groupby("grid_id", group_keys=False)

    out["rain_sum_3d"] = (
        group["primary_rain_sum"]
        .rolling(3, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    out["rain_sum_7d"] = (
        group["primary_rain_sum"]
        .rolling(7, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
    )

    out["wind_max_3d"] = (
        group["primary_wind_max"]
        .rolling(3, min_periods=1)
        .max()
        .reset_index(level=0, drop=True)
    )

    out["wind_max_7d"] = (
        group["primary_wind_max"]
        .rolling(7, min_periods=1)
        .max()
        .reset_index(level=0, drop=True)
    )

    out["humidity_min_3d"] = (
        group["primary_humidity_min"]
        .rolling(3, min_periods=1)
        .min()
        .reset_index(level=0, drop=True)
    )

    out["humidity_min_7d"] = (
        group["primary_humidity_min"]
        .rolling(7, min_periods=1)
        .min()
        .reset_index(level=0, drop=True)
    )

    out["temp_max_3d"] = (
        group["primary_temp_max"]
        .rolling(3, min_periods=1)
        .max()
        .reset_index(level=0, drop=True)
    )

    out["temp_max_7d"] = (
        group["primary_temp_max"]
        .rolling(7, min_periods=1)
        .max()
        .reset_index(level=0, drop=True)
    )

    def no_rain_days(series: pd.Series) -> pd.Series:
        result = []
        count = 0

        for v in series:
            if pd.isna(v):
                count = 0
                result.append(np.nan)
            elif v <= 0.1:
                count += 1
                result.append(count)
            else:
                count = 0
                result.append(0)

        return pd.Series(result, index=series.index)

    out["no_rain_days"] = (
        out.groupby("grid_id", group_keys=False)["primary_rain_sum"]
        .apply(no_rain_days)
    )

    return out


def make_report(df: pd.DataFrame, grid: pd.DataFrame, weather: pd.DataFrame):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    source_summary = (
        df.groupby("primary_weather_source", as_index=False)
        .agg(
            rows=("grid_id", "count"),
            grid_count=("grid_id", "nunique"),
        )
        .sort_values("rows", ascending=False)
    )

    date_summary = (
        df.groupby("date", as_index=False)
        .agg(
            rows=("grid_id", "count"),
            grid_count=("grid_id", "nunique"),
            aws_weather_rows=("has_aws_weather", "sum"),
            asos_weather_rows=("has_asos_weather", "sum"),
        )
        .sort_values("date")
    )

    distance_summary = df[
        [
            "primary_station_distance_m",
            "nearest_aws_distance_m",
            "nearest_asos_distance_m",
        ]
    ].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).reset_index()

    feature_summary_cols = [
        "primary_temp_mean",
        "primary_humidity_min",
        "primary_rain_sum",
        "primary_wind_max",
        "rain_sum_7d",
        "wind_max_7d",
        "humidity_min_7d",
        "no_rain_days",
    ]

    existing_feature_summary_cols = [c for c in feature_summary_cols if c in df.columns]
    feature_summary = df[existing_feature_summary_cols].describe().reset_index()

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Grid Day Features Report\n\n")

        f.write("## 1. Input Summary\n\n")
        f.write(f"- grid_station_rows: {len(grid)}\n")
        f.write(f"- weather_daily_rows: {len(weather)}\n")
        f.write(f"- weather_station_count: {weather['station_id'].nunique()}\n")
        f.write(f"- weather_date_min: {weather['date'].min()}\n")
        f.write(f"- weather_date_max: {weather['date'].max()}\n\n")

        f.write("## 2. Output Summary\n\n")
        f.write(f"- output: {OUT_PATH}\n")
        f.write(f"- output_rows: {len(df)}\n")
        f.write(f"- grid_count: {df['grid_id'].nunique()}\n")
        f.write(f"- date_count: {df['date'].nunique()}\n")
        f.write(f"- date_min: {df['date'].min()}\n")
        f.write(f"- date_max: {df['date'].max()}\n\n")

        f.write("## 3. Primary Weather Source\n\n")
        f.write(source_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 4. Date Coverage Sample\n\n")
        f.write(date_summary.head(15).to_markdown(index=False))
        f.write("\n\n")

        f.write("## 5. Distance Summary\n\n")
        f.write(distance_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 6. Feature Summary\n\n")
        f.write(feature_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 7. Output Columns\n\n")
        for c in df.columns:
            f.write(f"- {c}\n")


def main():
    grid, weather = load_inputs()

    print("Grid-station mapping:", grid.shape)
    print("Weather daily:", weather.shape)

    base = make_grid_date_base(grid, weather)
    print("Grid-date base:", base.shape)

    features = attach_weather(base, weather)
    features = add_primary_weather_features(features)
    features = add_rolling_features(features)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(OUT_PATH, index=False)

    make_report(features, grid, weather)

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print()
    print(features.head())
    print()
    print(features[["primary_weather_source", "has_aws_weather", "has_asos_weather"]].value_counts())


if __name__ == "__main__":
    main()
