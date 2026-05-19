from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]

IN_PATH = ROOT / "data" / "interim" / "poles_clean.parquet"
OUT_DIR = ROOT / "data" / "interim"
REPORT_DIR = ROOT / "reports"

OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

POLES_5179_PATH = OUT_DIR / "poles_5179.parquet"
GRID_ACTIVE_PATH = OUT_DIR / "grid_1km_active.parquet"
REPORT_PATH = REPORT_DIR / "grid_1km_profile_report.md"

GRID_SIZE_M = 1000


def main():
    if not IN_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {IN_PATH}")

    print("Loading:", IN_PATH)
    df = pd.read_parquet(IN_PATH)

    required = ["pole_id", "lon", "lat"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    print("Input shape:", df.shape)

    # EPSG:4326 lon/lat -> EPSG:5179 meter coordinate
    to_5179 = Transformer.from_crs("EPSG:4326", "EPSG:5179", always_xy=True)
    to_4326 = Transformer.from_crs("EPSG:5179", "EPSG:4326", always_xy=True)

    x, y = to_5179.transform(df["lon"].to_numpy(), df["lat"].to_numpy())

    out = df.copy()
    out["x_5179"] = x
    out["y_5179"] = y

    # 1km grid index
    out["grid_ix"] = np.floor(out["x_5179"] / GRID_SIZE_M).astype("int64")
    out["grid_iy"] = np.floor(out["y_5179"] / GRID_SIZE_M).astype("int64")
    out["grid_id"] = out["grid_ix"].astype(str) + "_" + out["grid_iy"].astype(str)

    print("Saving poles with grid:", POLES_5179_PATH)
    out.to_parquet(POLES_5179_PATH, index=False)

    # grid aggregation
    grid = (
        out.groupby(["grid_id", "grid_ix", "grid_iy"], as_index=False)
        .agg(
            pole_count=("pole_id", "count"),
            lon_mean=("lon", "mean"),
            lat_mean=("lat", "mean"),
        )
    )

    grid["x_min"] = grid["grid_ix"] * GRID_SIZE_M
    grid["y_min"] = grid["grid_iy"] * GRID_SIZE_M
    grid["x_max"] = grid["x_min"] + GRID_SIZE_M
    grid["y_max"] = grid["y_min"] + GRID_SIZE_M
    grid["x_center"] = grid["x_min"] + GRID_SIZE_M / 2
    grid["y_center"] = grid["y_min"] + GRID_SIZE_M / 2
    grid["grid_area_km2"] = (GRID_SIZE_M * GRID_SIZE_M) / 1_000_000
    grid["pole_density"] = grid["pole_count"] / grid["grid_area_km2"]

    # center lon/lat
    center_lon, center_lat = to_4326.transform(
        grid["x_center"].to_numpy(),
        grid["y_center"].to_numpy(),
    )
    grid["center_lon"] = center_lon
    grid["center_lat"] = center_lat

    # rectangle corner lon/lat for folium map
    sw_lon, sw_lat = to_4326.transform(
        grid["x_min"].to_numpy(),
        grid["y_min"].to_numpy(),
    )
    ne_lon, ne_lat = to_4326.transform(
        grid["x_max"].to_numpy(),
        grid["y_max"].to_numpy(),
    )
    grid["sw_lon"] = sw_lon
    grid["sw_lat"] = sw_lat
    grid["ne_lon"] = ne_lon
    grid["ne_lat"] = ne_lat

    grid = grid.sort_values("pole_count", ascending=False).reset_index(drop=True)

    print("Saving active grid:", GRID_ACTIVE_PATH)
    grid.to_parquet(GRID_ACTIVE_PATH, index=False)

    # report
    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Grid 1km Profile Report\n\n")
        f.write("## 1. Input\n\n")
        f.write(f"- input_file: {IN_PATH}\n")
        f.write(f"- input_rows: {len(df)}\n\n")

        f.write("## 2. Grid Settings\n\n")
        f.write("- source_crs: EPSG:4326\n")
        f.write("- analysis_crs: EPSG:5179\n")
        f.write(f"- grid_size_m: {GRID_SIZE_M}\n\n")

        f.write("## 3. Output Summary\n\n")
        f.write(f"- poles_5179_rows: {len(out)}\n")
        f.write(f"- active_grid_count: {len(grid)}\n")
        f.write(f"- total_pole_count_in_grid: {int(grid['pole_count'].sum())}\n")
        f.write(f"- pole_count_min: {int(grid['pole_count'].min())}\n")
        f.write(f"- pole_count_max: {int(grid['pole_count'].max())}\n")
        f.write(f"- pole_count_mean: {float(grid['pole_count'].mean())}\n")
        f.write(f"- pole_count_median: {float(grid['pole_count'].median())}\n\n")

        f.write("## 4. Top 20 Dense Grids\n\n")
        top20 = grid.head(20)[
            ["grid_id", "pole_count", "pole_density", "center_lon", "center_lat"]
        ]
        f.write(top20.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 5. Output Files\n\n")
        f.write(f"- poles_5179: {POLES_5179_PATH}\n")
        f.write(f"- grid_1km_active: {GRID_ACTIVE_PATH}\n")

    print()
    print("Done.")
    print("poles_5179:", POLES_5179_PATH)
    print("grid_1km_active:", GRID_ACTIVE_PATH)
    print("report:", REPORT_PATH)
    print()
    print("Grid count:", len(grid))
    print("Top grids:")
    print(grid.head(10)[["grid_id", "pole_count", "pole_density", "center_lon", "center_lat"]])


if __name__ == "__main__":
    main()
