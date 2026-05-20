from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INBOX = ROOT / "data" / "raw" / "_inbox"

TARGETS = {
    "OBS_AWS_TIM": ROOT / "data" / "raw" / "kma_aws" / "AWS_hourly_gangwon_202503.csv",
    "OBS_ASOS_TIM": ROOT / "data" / "raw" / "kma_asos" / "ASOS_hourly_gangwon_202503.csv",
    "OBS_ASOS_DD": ROOT / "data" / "raw" / "kma_asos" / "ASOS_daily_gangwon_202503.csv",
    "META_관측지점정보": ROOT / "data" / "raw" / "kma_station_meta" / "station_meta.csv",
    "FCT_WRN": ROOT / "data" / "raw" / "kma_warning" / "warning_dry_strongwind_202503.csv",
}

REPORT_PATH = ROOT / "reports" / "raw_standardization_report.md"

def find_source(prefix: str) -> Path:
    matches = sorted(INBOX.glob(f"{prefix}*.csv"))
    if not matches:
        raise FileNotFoundError(f"No file found for prefix: {prefix}")
    return matches[0]

def read_cp949(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="cp949")

def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for prefix, target in TARGETS.items():
        source = find_source(prefix)
        target.parent.mkdir(parents=True, exist_ok=True)

        df = read_cp949(source)
        df.to_csv(target, index=False, encoding="utf-8-sig")

        rows.append({
            "prefix": prefix,
            "source": str(source.relative_to(ROOT)),
            "target": str(target.relative_to(ROOT)),
            "rows": len(df),
            "cols": len(df.columns),
            "columns": " | ".join(map(str, df.columns)),
        })

        print(f"[OK] {source.name} -> {target}")
        print(f"     rows={len(df)}, cols={len(df.columns)}")

    report_df = pd.DataFrame(rows)

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Raw Standardization Report\n\n")
        f.write("## Summary\n\n")
        f.write(report_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## Critical Check\n\n")
        meta = report_df[report_df["prefix"] == "META_관측지점정보"]
        if not meta.empty and int(meta.iloc[0]["rows"]) == 0:
            f.write("- WARNING: station_meta.csv has 0 rows. 관측소 좌표 매칭이 불가능하므로 메타데이터 재다운로드가 필요합니다.\n")
        else:
            f.write("- station_meta.csv row count is valid.\n")

    print("Saved report:", REPORT_PATH)

if __name__ == "__main__":
    main()
