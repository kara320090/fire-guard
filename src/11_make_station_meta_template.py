from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

IN_PATH = ROOT / "data/interim/station_list_needed.csv"
OUT_PATH = ROOT / "data/raw/kma_station_meta/station_meta_manual_template.csv"

def main():
    station = pd.read_csv(IN_PATH, encoding="utf-8-sig")

    out = station.rename(columns={
        "지점": "station_id",
        "지점명": "station_name",
    }).copy()

    out["lat"] = ""
    out["lon"] = ""
    out["altitude_m"] = ""
    out["meta_source"] = "manual_or_kma_station_page"
    out["note"] = ""

    out = out[[
        "station_id",
        "station_name",
        "lat",
        "lon",
        "altitude_m",
        "source",
        "meta_source",
        "note",
    ]]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print("Saved:", OUT_PATH)
    print(out.head(30))

if __name__ == "__main__":
    main()
