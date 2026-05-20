from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

NEEDED_PATH = ROOT / "data/interim/station_list_needed.csv"

META_STATIC_CANDIDATES = [
    ROOT / "data/raw/kma_station_meta/station_meta.csv",
    ROOT / "data/raw/kma_station_meta/station_meta_asos.csv",
    ROOT / "data/raw/kma_station_meta/station_meta_aws.csv",
]

META_GLOB_CANDIDATES = [
    ROOT / "data/raw/_inbox",
    ROOT / "data/raw/kma_station_meta",
]

OUT_PATH = ROOT / "data/interim/station_meta_active_202503.csv"
REPORT_PATH = ROOT / "reports/station_meta_active_report.md"

TARGET_START = pd.Timestamp("2025-03-01")
TARGET_END = pd.Timestamp("2025-03-31")


def collect_meta_candidates() -> list[Path]:
    paths = []

    for p in META_STATIC_CANDIDATES:
        if p.exists():
            paths.append(p)

    for folder in META_GLOB_CANDIDATES:
        if folder.exists():
            paths.extend(folder.glob("META*.csv"))
            paths.extend(folder.glob("*관측지점*.csv"))
            paths.extend(folder.glob("*station_meta*.csv"))

    # 중복 제거
    unique = []
    seen = set()
    for p in paths:
        rp = p.resolve()
        if rp not in seen:
            unique.append(p)
            seen.add(rp)

    return unique


def read_meta_file(path: Path) -> pd.DataFrame | None:
    for enc in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            print(f"[READ] {path} | encoding={enc} | shape={df.shape}")
            if len(df) == 0:
                return None
            return df
        except Exception:
            continue

    print(f"[FAIL] cannot read: {path}")
    return None


def normalize_columns(df: pd.DataFrame, source_file: str) -> pd.DataFrame:
    col_map = {
        "지점": "station_id",
        "지점명": "station_name_raw",
        "시작일": "start_date",
        "종료일": "end_date",
        "위도": "lat",
        "경도": "lon",
        "노장해발고도(m)": "altitude_m",
    }

    missing = [c for c in col_map.keys() if c not in df.columns]
    if missing:
        print("[WARN] missing columns:", missing)
        print("[WARN] actual columns:", list(df.columns))

    rename_map = {k: v for k, v in col_map.items() if k in df.columns}
    out = df.rename(columns=rename_map).copy()

    required = ["station_id", "lat", "lon"]
    missing_required = [c for c in required if c not in out.columns]
    if missing_required:
        print(f"[SKIP] {source_file} missing required after normalize:", missing_required)
        return pd.DataFrame()

    keep_cols = [
        c for c in [
            "station_id",
            "station_name_raw",
            "start_date",
            "end_date",
            "lat",
            "lon",
            "altitude_m",
        ]
        if c in out.columns
    ]

    out = out[keep_cols].copy()
    out["source_file"] = source_file

    out["station_id"] = pd.to_numeric(out["station_id"], errors="coerce").astype("Int64")
    out["lat"] = pd.to_numeric(out["lat"], errors="coerce")
    out["lon"] = pd.to_numeric(out["lon"], errors="coerce")

    if "altitude_m" in out.columns:
        out["altitude_m"] = pd.to_numeric(out["altitude_m"], errors="coerce")
    else:
        out["altitude_m"] = pd.NA

    if "start_date" in out.columns:
        out["start_date"] = pd.to_datetime(out["start_date"], errors="coerce")
    else:
        out["start_date"] = pd.NaT

    if "end_date" in out.columns:
        out["end_date"] = pd.to_datetime(out["end_date"], errors="coerce")
    else:
        out["end_date"] = pd.NaT

    return out


def main():
    if not NEEDED_PATH.exists():
        raise FileNotFoundError(f"Missing station list: {NEEDED_PATH}")

    needed = pd.read_csv(NEEDED_PATH, encoding="utf-8-sig")
    needed = needed.rename(columns={"지점": "station_id", "지점명": "station_name"})
    needed["station_id"] = pd.to_numeric(needed["station_id"], errors="coerce").astype("Int64")

    candidates = collect_meta_candidates()

    print("META candidate files:")
    for p in candidates:
        print(" -", p)

    meta_frames = []

    for path in candidates:
        df = read_meta_file(path)
        if df is None or len(df) == 0:
            print("[SKIP empty]", path)
            continue

        norm = normalize_columns(df, source_file=str(path.relative_to(ROOT)))
        if len(norm) > 0:
            meta_frames.append(norm)

    if not meta_frames:
        raise RuntimeError(
            "No valid station metadata files found. "
            "Check data/raw/_inbox/META*.csv or data/raw/kma_station_meta/*.csv"
        )

    meta = pd.concat(meta_frames, ignore_index=True)

    # 좌표 결측 제거
    meta = meta.dropna(subset=["station_id", "lat", "lon"]).copy()

    # 2025-03 기준 유효한 관측소 이력만 선택
    active = meta[
        (meta["start_date"].isna() | (meta["start_date"] <= TARGET_END))
        & (meta["end_date"].isna() | (meta["end_date"] >= TARGET_START))
    ].copy()

    active["end_is_open"] = active["end_date"].isna().astype(int)

    active = active.sort_values(
        ["station_id", "end_is_open", "start_date"],
        ascending=[True, False, False],
    )

    active = active.drop_duplicates(subset=["station_id"], keep="first").copy()

    out = needed.merge(
        active[
            [
                "station_id",
                "lat",
                "lon",
                "altitude_m",
                "start_date",
                "end_date",
                "source_file",
            ]
        ],
        on="station_id",
        how="left",
    )

    out["has_coord"] = out["lat"].notna() & out["lon"].notna()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    missing = out[~out["has_coord"]].copy()

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Station Meta Active Report\\n\\n")
        f.write("## Summary\\n\\n")
        f.write(f"- target_period: {TARGET_START.date()} ~ {TARGET_END.date()}\\n")
        f.write(f"- needed_station_count: {len(needed)}\\n")
        f.write(f"- candidate_file_count: {len(candidates)}\\n")
        f.write(f"- normalized_meta_rows: {len(meta)}\\n")
        f.write(f"- active_meta_count: {len(active)}\\n")
        f.write(f"- output_rows: {len(out)}\\n")
        f.write(f"- matched_coord_count: {int(out['has_coord'].sum())}\\n")
        f.write(f"- missing_coord_count: {int((~out['has_coord']).sum())}\\n\\n")

        f.write("## Candidate Files\\n\\n")
        for p in candidates:
            f.write(f"- {p.relative_to(ROOT)}\\n")

        f.write("\\n## Missing Coordinates\\n\\n")
        if len(missing) == 0:
            f.write("No missing coordinates.\\n")
        else:
            f.write(missing[["station_id", "station_name", "source"]].to_markdown(index=False))
            f.write("\\n")

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print("matched:", int(out["has_coord"].sum()), "/", len(out))

    if len(missing) > 0:
        print("Missing:")
        print(missing[["station_id", "station_name", "source"]].head(50))


if __name__ == "__main__":
    main()
