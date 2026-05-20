from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "aws_hourly": ROOT / "data/raw/_inbox/OBS_AWS_TIM_20260519211355.csv",
    "asos_hourly": ROOT / "data/raw/_inbox/OBS_ASOS_TIM_20260519211904.csv",
    "asos_daily": ROOT / "data/raw/_inbox/OBS_ASOS_DD_20260519212046.csv",
}

OUT_PATH = ROOT / "data/interim/station_list_needed.csv"
REPORT_PATH = ROOT / "reports/station_list_needed_report.md"

def read_csv(path):
    return pd.read_csv(path, encoding="cp949")

def main():
    rows = []

    for source_name, path in FILES.items():
        if not path.exists():
            print("MISSING:", path)
            continue

        df = read_csv(path)

        if "지점" not in df.columns or "지점명" not in df.columns:
            print("SKIP:", source_name, "missing 지점/지점명")
            continue

        tmp = df[["지점", "지점명"]].drop_duplicates().copy()
        tmp["source"] = source_name
        rows.append(tmp)

    if not rows:
        raise RuntimeError("No station rows found.")

    all_stations = pd.concat(rows, ignore_index=True)

    station = (
        all_stations
        .groupby(["지점", "지점명"], as_index=False)
        .agg(source=("source", lambda x: ",".join(sorted(set(x)))))
        .sort_values(["source", "지점"])
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    station.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Station List Needed Report\n\n")
        f.write(f"- output: {OUT_PATH}\n")
        f.write(f"- station_count: {len(station)}\n\n")
        f.write("## Stations\n\n")
        f.write(station.to_markdown(index=False))

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print("station_count:", len(station))
    print(station.head(30))

if __name__ == "__main__":
    main()
