from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

AWS_PATH = ROOT / "data/raw/kma_aws/AWS_hourly_gangwon_202503.csv"
ASOS_HOURLY_PATH = ROOT / "data/raw/kma_asos/ASOS_hourly_gangwon_202503.csv"
ASOS_DAILY_PATH = ROOT / "data/raw/kma_asos/ASOS_daily_gangwon_202503.csv"

OUT_PATH = ROOT / "data/interim/weather_daily_202503.parquet"
REPORT_PATH = ROOT / "reports/weather_daily_report.md"

ENCODINGS = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]


def read_csv_auto(path: Path) -> tuple[pd.DataFrame, str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    errors = []

    for enc in ENCODINGS:
        try:
            df = pd.read_csv(path, encoding=enc)
            print(f"[READ OK] {path.name} | encoding={enc} | shape={df.shape}")
            return df, enc
        except Exception as e:
            errors.append(f"{enc}: {type(e).__name__}: {e}")

    raise RuntimeError(
        f"Cannot read CSV: {path}\n"
        + "\n".join(errors)
    )


def require_columns(df: pd.DataFrame, required: list[str], name: str):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing columns: {missing}\nActual columns: {list(df.columns)}")


def parse_wind_dir(df: pd.DataFrame) -> pd.Series:
    if "풍향(deg)" in df.columns:
        return pd.to_numeric(df["풍향(deg)"], errors="coerce")

    if "풍향(16방위)" in df.columns:
        raw = pd.to_numeric(df["풍향(16방위)"], errors="coerce")

        # 값이 0~16 수준이면 16방위 코드로 보고 degree로 변환
        # 값이 이미 0~360이면 그대로 사용
        if raw.dropna().max() <= 16:
            return raw * 22.5
        return raw

    return pd.Series(np.nan, index=df.index)


def standardize_hourly(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    require_columns(df, ["지점", "지점명", "일시"], source_type)

    out = pd.DataFrame()

    out["station_id"] = pd.to_numeric(df["지점"], errors="coerce").astype("Int64")
    out["station_name"] = df["지점명"].astype(str)
    out["datetime"] = pd.to_datetime(df["일시"], errors="coerce")
    out["date"] = out["datetime"].dt.floor("D")

    out["temp"] = pd.to_numeric(df.get("기온(°C)"), errors="coerce")
    out["humidity"] = pd.to_numeric(df.get("습도(%)"), errors="coerce")
    out["rain"] = pd.to_numeric(df.get("강수량(mm)"), errors="coerce").fillna(0)
    out["wind_speed"] = pd.to_numeric(df.get("풍속(m/s)"), errors="coerce")
    out["wind_dir"] = parse_wind_dir(df)

    if "현지기압(hPa)" in df.columns:
        out["pressure"] = pd.to_numeric(df["현지기압(hPa)"], errors="coerce")
    else:
        out["pressure"] = np.nan

    out["source_type"] = source_type

    out = out.dropna(subset=["station_id", "datetime", "date"]).copy()

    # 비정상 좌표/시간 제거용은 아니고, 관측값 없는 행만 그대로 NaN 유지
    return out


def aggregate_daily(hourly: pd.DataFrame) -> pd.DataFrame:
    daily = (
        hourly.groupby(["station_id", "station_name", "date", "source_type"], as_index=False)
        .agg(
            temp_mean=("temp", "mean"),
            temp_max=("temp", "max"),
            temp_min=("temp", "min"),
            humidity_mean=("humidity", "mean"),
            humidity_min=("humidity", "min"),
            rain_sum=("rain", "sum"),
            wind_mean=("wind_speed", "mean"),
            wind_max=("wind_speed", "max"),
            wind_dir_mean=("wind_dir", "mean"),
            pressure_mean=("pressure", "mean"),
            row_count=("datetime", "count"),
            temp_obs_count=("temp", "count"),
            humidity_obs_count=("humidity", "count"),
            wind_obs_count=("wind_speed", "count"),
            rain_obs_count=("rain", "count"),
        )
    )

    daily["date"] = pd.to_datetime(daily["date"])
    return daily


def main():
    aws, aws_enc = read_csv_auto(AWS_PATH)
    asos_h, asos_enc = read_csv_auto(ASOS_HOURLY_PATH)

    # ASOS 일자료는 이번 단계에서 직접 결합하지 않고,
    # 시간자료 기반 일집계 결과 검증용으로만 profile에 기록
    asos_d_shape = None
    asos_d_enc = None
    if ASOS_DAILY_PATH.exists():
        asos_d, asos_d_enc = read_csv_auto(ASOS_DAILY_PATH)
        asos_d_shape = asos_d.shape

    aws_std = standardize_hourly(aws, "aws")
    asos_std = standardize_hourly(asos_h, "asos")

    hourly_all = pd.concat([aws_std, asos_std], ignore_index=True)
    daily = aggregate_daily(hourly_all)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    daily.to_parquet(OUT_PATH, index=False)

    summary = (
        daily.groupby("source_type")
        .agg(
            station_count=("station_id", "nunique"),
            rows=("station_id", "count"),
            date_min=("date", "min"),
            date_max=("date", "max"),
            mean_row_count=("row_count", "mean"),
            min_row_count=("row_count", "min"),
            max_row_count=("row_count", "max"),
        )
        .reset_index()
    )

    date_station_summary = (
        daily.groupby("date")
        .agg(
            station_count=("station_id", "nunique"),
            rows=("station_id", "count"),
        )
        .reset_index()
    )

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Weather Daily Report\n\n")

        f.write("## 1. Input Encoding\n\n")
        f.write(f"- AWS hourly encoding: {aws_enc}\n")
        f.write(f"- ASOS hourly encoding: {asos_enc}\n")
        f.write(f"- ASOS daily encoding: {asos_d_enc}\n")
        f.write(f"- ASOS daily shape: {asos_d_shape}\n\n")

        f.write("## 2. Output Summary\n\n")
        f.write(f"- output: {OUT_PATH}\n")
        f.write(f"- rows: {len(daily)}\n")
        f.write(f"- station_count: {daily['station_id'].nunique()}\n")
        f.write(f"- date_min: {daily['date'].min()}\n")
        f.write(f"- date_max: {daily['date'].max()}\n\n")

        f.write("## 3. By Source Type\n\n")
        f.write(summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 4. Date Coverage Sample\n\n")
        f.write(date_station_summary.head(10).to_markdown(index=False))
        f.write("\n\n")

        f.write("## 5. Columns\n\n")
        for c in daily.columns:
            f.write(f"- {c}\n")

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print()
    print(daily.head())
    print()
    print(summary)


if __name__ == "__main__":
    main()
