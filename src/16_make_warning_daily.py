from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

WARNING_PATH = ROOT / "data/raw/kma_warning/warning_dry_strongwind_202503.csv"
OUT_PATH = ROOT / "data/interim/warning_daily_202503.parquet"
REPORT_PATH = ROOT / "reports/warning_daily_report.md"

TARGET_START = pd.Timestamp("2025-03-01")
TARGET_END = pd.Timestamp("2025-03-31")

ENCODINGS = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]


def read_csv_auto(path: Path) -> tuple[pd.DataFrame, str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing warning file: {path}")

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


def find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = list(df.columns)

    for cand in candidates:
        if cand in cols:
            return cand

    for col in cols:
        col_str = str(col)
        for cand in candidates:
            if cand in col_str:
                return col

    return None


def build_row_text(df: pd.DataFrame) -> pd.Series:
    text_cols = []
    for c in df.columns:
        if df[c].dtype == "object" or str(df[c].dtype).startswith("string"):
            text_cols.append(c)

    if not text_cols:
        return pd.Series([""] * len(df), index=df.index)

    return df[text_cols].fillna("").astype(str).agg(" ".join, axis=1)


def normalize_warning(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    announce_col = find_col(out, ["발표시각", "발표시간", "발표 일시", "발표일시"])
    effective_col = find_col(out, ["발효시각", "발효시간", "발효 일시", "발효일시"])
    release_col = find_col(out, ["해제시각", "해제시간", "해제 일시", "해제일시"])
    region_col = find_col(out, ["구역", "특보구역", "지역", "지점명", "구역명"])
    type_col = find_col(out, ["특보종류", "종류", "특보명"])
    level_col = find_col(out, ["특보수준", "수준", "주의보", "경보"])

    row_text = build_row_text(out)

    # 날짜 기준은 발효시각 우선, 없으면 발표시각
    if effective_col is not None:
        dt = pd.to_datetime(out[effective_col], errors="coerce")
    elif announce_col is not None:
        dt = pd.to_datetime(out[announce_col], errors="coerce")
    else:
        # 날짜 컬럼을 못 찾으면 모든 row를 target 기간으로 보낼 수 없으므로 NaT 처리
        dt = pd.Series(pd.NaT, index=out.index)

    # 발효시각이 전부 NaT면 발표시각으로 fallback
    if dt.notna().sum() == 0 and announce_col is not None:
        dt = pd.to_datetime(out[announce_col], errors="coerce")

    norm = pd.DataFrame()
    norm["event_datetime"] = dt
    norm["date"] = norm["event_datetime"].dt.floor("D")

    norm["row_text"] = row_text

    if region_col is not None:
        norm["region_text"] = out[region_col].fillna("").astype(str)
    else:
        norm["region_text"] = ""

    if type_col is not None:
        norm["warning_type"] = out[type_col].fillna("").astype(str)
    else:
        norm["warning_type"] = ""

    if level_col is not None:
        norm["warning_level"] = out[level_col].fillna("").astype(str)
    else:
        norm["warning_level"] = ""

    full_text = (
        norm["row_text"].fillna("").astype(str)
        + " "
        + norm["warning_type"].fillna("").astype(str)
        + " "
        + norm["warning_level"].fillna("").astype(str)
        + " "
        + norm["region_text"].fillna("").astype(str)
    )

    norm["is_dry"] = full_text.str.contains("건조", regex=False)
    norm["is_strong_wind"] = full_text.str.contains("강풍", regex=False)

    norm["is_warning"] = full_text.str.contains("주의보", regex=False)
    norm["is_alert"] = full_text.str.contains("경보", regex=False)

    norm["dry_warning_level_score"] = np.select(
        [
            norm["is_dry"] & norm["is_alert"],
            norm["is_dry"] & norm["is_warning"],
            norm["is_dry"],
        ],
        [2, 1, 1],
        default=0,
    )

    norm["strong_wind_level_score"] = np.select(
        [
            norm["is_strong_wind"] & norm["is_alert"],
            norm["is_strong_wind"] & norm["is_warning"],
            norm["is_strong_wind"],
        ],
        [2, 1, 1],
        default=0,
    )

    return norm


def make_daily_warning(norm: pd.DataFrame) -> pd.DataFrame:
    # 날짜가 있는 row만 사용
    valid = norm.dropna(subset=["date"]).copy()

    # 2025-03 범위만 사용
    valid = valid[(valid["date"] >= TARGET_START) & (valid["date"] <= TARGET_END)].copy()

    all_dates = pd.date_range(TARGET_START, TARGET_END, freq="D")
    base = pd.DataFrame({"date": all_dates})

    if len(valid) == 0:
        base["dry_warning_flag"] = 0
        base["strong_wind_warning_flag"] = 0
        base["dry_warning_count"] = 0
        base["strong_wind_warning_count"] = 0
        base["dry_warning_level_max"] = 0
        base["strong_wind_level_max"] = 0
        base["dry_and_windy_warning_flag"] = 0
        base["warning_event_count"] = 0
        return base

    daily = (
        valid.groupby("date", as_index=False)
        .agg(
            dry_warning_count=("is_dry", "sum"),
            strong_wind_warning_count=("is_strong_wind", "sum"),
            dry_warning_level_max=("dry_warning_level_score", "max"),
            strong_wind_level_max=("strong_wind_level_score", "max"),
            warning_event_count=("row_text", "count"),
            warning_regions=("region_text", lambda x: " | ".join(sorted(set(map(str, x))))[:1000]),
        )
    )

    out = base.merge(daily, on="date", how="left")

    fill_zero_cols = [
        "dry_warning_count",
        "strong_wind_warning_count",
        "dry_warning_level_max",
        "strong_wind_level_max",
        "warning_event_count",
    ]

    for c in fill_zero_cols:
        out[c] = out[c].fillna(0).astype(int)

    out["warning_regions"] = out["warning_regions"].fillna("")

    out["dry_warning_flag"] = (out["dry_warning_count"] > 0).astype(int)
    out["strong_wind_warning_flag"] = (out["strong_wind_warning_count"] > 0).astype(int)
    out["dry_and_windy_warning_flag"] = (
        (out["dry_warning_flag"] == 1)
        & (out["strong_wind_warning_flag"] == 1)
    ).astype(int)

    out = out[
        [
            "date",
            "dry_warning_flag",
            "strong_wind_warning_flag",
            "dry_and_windy_warning_flag",
            "dry_warning_count",
            "strong_wind_warning_count",
            "dry_warning_level_max",
            "strong_wind_level_max",
            "warning_event_count",
            "warning_regions",
        ]
    ]

    return out


def main():
    raw, enc = read_csv_auto(WARNING_PATH)
    norm = normalize_warning(raw)
    daily = make_daily_warning(norm)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    daily.to_parquet(OUT_PATH, index=False)

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Warning Daily Report\n\n")

        f.write("## 1. Input Summary\n\n")
        f.write(f"- input: {WARNING_PATH}\n")
        f.write(f"- encoding: {enc}\n")
        f.write(f"- raw_rows: {len(raw)}\n")
        f.write(f"- raw_columns: {list(raw.columns)}\n\n")

        f.write("## 2. Normalized Summary\n\n")
        f.write(f"- normalized_rows: {len(norm)}\n")
        f.write(f"- valid_date_rows: {int(norm['date'].notna().sum())}\n")
        f.write(f"- dry_rows: {int(norm['is_dry'].sum())}\n")
        f.write(f"- strong_wind_rows: {int(norm['is_strong_wind'].sum())}\n\n")

        f.write("## 3. Daily Output Summary\n\n")
        f.write(f"- output: {OUT_PATH}\n")
        f.write(f"- rows: {len(daily)}\n")
        f.write(f"- date_min: {daily['date'].min()}\n")
        f.write(f"- date_max: {daily['date'].max()}\n")
        f.write(f"- dry_warning_days: {int(daily['dry_warning_flag'].sum())}\n")
        f.write(f"- strong_wind_warning_days: {int(daily['strong_wind_warning_flag'].sum())}\n")
        f.write(f"- dry_and_windy_warning_days: {int(daily['dry_and_windy_warning_flag'].sum())}\n\n")

        f.write("## 4. Daily Table\n\n")
        f.write(daily.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 5. Normalized Preview\n\n")
        preview_cols = [
            "date",
            "region_text",
            "warning_type",
            "warning_level",
            "is_dry",
            "is_strong_wind",
            "dry_warning_level_score",
            "strong_wind_level_score",
        ]
        existing = [c for c in preview_cols if c in norm.columns]
        f.write(norm[existing].head(30).to_markdown(index=False))
        f.write("\n")

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print()
    print(daily)


if __name__ == "__main__":
    main()
