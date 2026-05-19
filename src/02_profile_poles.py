from pathlib import Path
import zipfile
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

ZIP_PATH = ROOT / "data" / "raw" / "contest" / "contest_data_1.zip"
INTERIM_DIR = ROOT / "data" / "interim"
REPORT_DIR = ROOT / "reports"

INTERIM_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RAW_PREVIEW_PATH = INTERIM_DIR / "poles_raw_preview.csv"
CLEAN_PATH = INTERIM_DIR / "poles_clean.parquet"
REPORT_PATH = REPORT_DIR / "poles_profile_report.md"


def find_csv_in_zip(zip_path: Path) -> str:
    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

    csv_files = [name for name in names if name.lower().endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError("ZIP 내부에서 CSV 파일을 찾지 못했습니다.")

    # 일반적으로 hanjeon/gangwon_poles_4326.csv 하나가 잡혀야 합니다.
    print("CSV candidates:")
    for item in csv_files:
        print(" -", item)

    return csv_files[0]


def load_poles_csv(zip_path: Path, csv_name: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(csv_name) as f:
            df = pd.read_csv(
                f,
                dtype={
                    "pole_id": "string",
                },
            )

    return df


def profile_dataframe(df: pd.DataFrame) -> dict:
    report = {}

    report["rows_raw"] = int(len(df))
    report["columns"] = list(df.columns)

    required_cols = ["pole_id", "lon", "lat"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    report["missing_required_columns"] = missing_cols

    if missing_cols:
        return report

    # lon/lat 숫자 변환 가능성 확인
    lon_numeric = pd.to_numeric(df["lon"], errors="coerce")
    lat_numeric = pd.to_numeric(df["lat"], errors="coerce")

    report["pole_id_missing"] = int(df["pole_id"].isna().sum())
    report["lon_missing_or_invalid"] = int(lon_numeric.isna().sum())
    report["lat_missing_or_invalid"] = int(lat_numeric.isna().sum())

    report["pole_id_duplicates"] = int(df["pole_id"].duplicated().sum())

    report["lon_min"] = float(lon_numeric.min())
    report["lon_max"] = float(lon_numeric.max())
    report["lat_min"] = float(lat_numeric.min())
    report["lat_max"] = float(lat_numeric.max())

    # 대한민국 전체를 대략 포함하는 위경도 범위로 1차 이상치만 확인
    rough_korea_bbox = (
        lon_numeric.between(124.0, 132.5)
        & lat_numeric.between(33.0, 39.5)
    )

    report["rough_korea_bbox_outliers"] = int((~rough_korea_bbox).sum())

    # 강원도 대략 범위. 너무 엄격하게 자르지는 않고 참고용으로만 기록.
    rough_gangwon_bbox = (
        lon_numeric.between(127.0, 130.0)
        & lat_numeric.between(37.0, 38.8)
    )

    report["rough_gangwon_bbox_outliers_reference_only"] = int((~rough_gangwon_bbox).sum())

    return report


def make_clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required_cols = ["pole_id", "lon", "lat"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼이 없습니다: {col}")

    clean = df[required_cols].copy()

    clean["pole_id"] = clean["pole_id"].astype("string")
    clean["lon"] = pd.to_numeric(clean["lon"], errors="coerce")
    clean["lat"] = pd.to_numeric(clean["lat"], errors="coerce")

    rows_before = len(clean)

    # 필수값 결측 제거
    clean = clean.dropna(subset=["pole_id", "lon", "lat"]).copy()

    # 대한민국 전체 범위 밖 좌표 제거
    clean = clean[
        clean["lon"].between(124.0, 132.5)
        & clean["lat"].between(33.0, 39.5)
    ].copy()

    # pole_id 중복 제거
    clean = clean.drop_duplicates(subset=["pole_id"], keep="first").copy()

    rows_after = len(clean)
    print(f"Clean rows: {rows_before:,} -> {rows_after:,}")

    return clean


def write_report(report: dict, clean_df: pd.DataFrame, csv_name: str) -> None:
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Poles Profile Report\n\n")

        f.write("## 1. Source\n\n")
        f.write(f"- ZIP: {ZIP_PATH}\n")
        f.write(f"- CSV inside ZIP: {csv_name}\n\n")

        f.write("## 2. Raw Data Profile\n\n")
        for key, value in report.items():
            f.write(f"- {key}: {value}\n")

        f.write("\n## 3. Clean Data Profile\n\n")
        f.write(f"- rows_clean: {len(clean_df)}\n")
        f.write(f"- columns_clean: {list(clean_df.columns)}\n")
        f.write(f"- lon_min_clean: {clean_df['lon'].min()}\n")
        f.write(f"- lon_max_clean: {clean_df['lon'].max()}\n")
        f.write(f"- lat_min_clean: {clean_df['lat'].min()}\n")
        f.write(f"- lat_max_clean: {clean_df['lat'].max()}\n")

        f.write("\n## 4. Output Files\n\n")
        f.write(f"- raw preview: {RAW_PREVIEW_PATH}\n")
        f.write(f"- clean parquet: {CLEAN_PATH}\n")

        f.write("\n## 5. Notes\n\n")
        f.write("- 원본 좌표계는 파일명 기준 EPSG:4326으로 추정합니다.\n")
        f.write("- 거리, buffer, grid 계산 전에는 EPSG:5179 또는 EPSG:5186으로 변환해야 합니다.\n")
        f.write("- rough_gangwon_bbox_outliers_reference_only는 참고용이며, 실제 제거 기준으로 사용하지 않았습니다.\n")


def main():
    print("ROOT:", ROOT)
    print("ZIP_PATH:", ZIP_PATH)

    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"ZIP 파일이 없습니다: {ZIP_PATH}")

    csv_name = find_csv_in_zip(ZIP_PATH)
    df = load_poles_csv(ZIP_PATH, csv_name)

    print("Raw shape:", df.shape)
    print("Columns:", list(df.columns))
    print(df.head())

    df.head(1000).to_csv(RAW_PREVIEW_PATH, index=False, encoding="utf-8-sig")

    report = profile_dataframe(df)

    if report.get("missing_required_columns"):
        raise ValueError(f"필수 컬럼 누락: {report['missing_required_columns']}")

    clean = make_clean_dataframe(df)
    clean.to_parquet(CLEAN_PATH, index=False)

    write_report(report, clean, csv_name)

    print()
    print("Saved raw preview:", RAW_PREVIEW_PATH)
    print("Saved clean parquet:", CLEAN_PATH)
    print("Saved report:", REPORT_PATH)


if __name__ == "__main__":
    main()
