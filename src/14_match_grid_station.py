from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]

GRID_PATH = ROOT / "data/interim/grid_1km_active.parquet"
STATION_PATH = ROOT / "data/interim/station_meta_active_202503.csv"

OUT_PATH = ROOT / "data/interim/grid_station_mapping_202503.parquet"
REPORT_PATH = ROOT / "reports/grid_station_mapping_report.md"

TO_5179 = Transformer.from_crs("EPSG:4326", "EPSG:5179", always_xy=True)


def load_grid() -> pd.DataFrame:
    if not GRID_PATH.exists():
        raise FileNotFoundError(f"Missing grid file: {GRID_PATH}")

    grid = pd.read_parquet(GRID_PATH)

    required = ["grid_id", "center_lon", "center_lat", "x_center", "y_center", "pole_count"]
    missing = [c for c in required if c not in grid.columns]
    if missing:
        raise ValueError(f"Grid missing columns: {missing}")

    return grid


def load_station() -> pd.DataFrame:
    if not STATION_PATH.exists():
        raise FileNotFoundError(f"Missing station file: {STATION_PATH}")

    st = pd.read_csv(STATION_PATH, encoding="utf-8-sig")

    required = ["station_id", "station_name", "source", "lat", "lon", "has_coord"]
    missing = [c for c in required if c not in st.columns]
    if missing:
        raise ValueError(f"Station missing columns: {missing}")

    st = st[st["has_coord"].astype(str).str.lower().isin(["true", "1"])].copy()

    st["station_id"] = pd.to_numeric(st["station_id"], errors="coerce").astype("Int64")
    st["lat"] = pd.to_numeric(st["lat"], errors="coerce")
    st["lon"] = pd.to_numeric(st["lon"], errors="coerce")

    st = st.dropna(subset=["station_id", "lat", "lon"]).copy()

    st["station_source_type"] = np.where(
        st["source"].astype(str).str.contains("aws", case=False, na=False),
        "aws",
        "asos",
    )

    sx, sy = TO_5179.transform(st["lon"].to_numpy(), st["lat"].to_numpy())
    st["x_5179"] = sx
    st["y_5179"] = sy

    return st


def nearest_station_for_group(grid: pd.DataFrame, stations: pd.DataFrame, prefix: str) -> pd.DataFrame:
    if len(stations) == 0:
        raise ValueError(f"No stations for prefix={prefix}")

    gx = grid["x_center"].to_numpy(dtype=float)
    gy = grid["y_center"].to_numpy(dtype=float)

    sx = stations["x_5179"].to_numpy(dtype=float)
    sy = stations["y_5179"].to_numpy(dtype=float)

    # 9908 x 102 정도라 메모리 부담 없음
    dx = gx[:, None] - sx[None, :]
    dy = gy[:, None] - sy[None, :]
    dist = np.sqrt(dx * dx + dy * dy)

    idx = dist.argmin(axis=1)
    min_dist = dist[np.arange(len(grid)), idx]

    nearest = stations.iloc[idx].reset_index(drop=True)

    out = pd.DataFrame({
        "grid_id": grid["grid_id"].to_numpy(),
        f"nearest_{prefix}_station_id": nearest["station_id"].astype("Int64"),
        f"nearest_{prefix}_station_name": nearest["station_name"].astype(str),
        f"nearest_{prefix}_station_source": nearest["station_source_type"].astype(str),
        f"nearest_{prefix}_station_lon": nearest["lon"].astype(float),
        f"nearest_{prefix}_station_lat": nearest["lat"].astype(float),
        f"nearest_{prefix}_distance_m": min_dist,
    })

    return out


def main():
    grid = load_grid()
    station = load_station()

    aws_st = station[station["station_source_type"] == "aws"].copy()
    asos_st = station[station["station_source_type"] == "asos"].copy()

    print("Grid:", grid.shape)
    print("Stations:", station.shape)
    print("AWS stations:", len(aws_st))
    print("ASOS stations:", len(asos_st))

    base = grid[[
        "grid_id",
        "grid_ix",
        "grid_iy",
        "pole_count",
        "pole_density",
        "center_lon",
        "center_lat",
        "x_center",
        "y_center",
    ]].copy()

    nearest_all = nearest_station_for_group(grid, station, "any")
    nearest_aws = nearest_station_for_group(grid, aws_st, "aws")
    nearest_asos = nearest_station_for_group(grid, asos_st, "asos")

    out = base.merge(nearest_all, on="grid_id", how="left")
    out = out.merge(nearest_aws, on="grid_id", how="left")
    out = out.merge(nearest_asos, on="grid_id", how="left")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    out.to_parquet(OUT_PATH, index=False)

    distance_cols = [
        "nearest_any_distance_m",
        "nearest_aws_distance_m",
        "nearest_asos_distance_m",
    ]

    distance_summary = out[distance_cols].describe(
        percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    ).reset_index()

    aws_usage = (
        out.groupby(["nearest_aws_station_id", "nearest_aws_station_name"], as_index=False)
        .agg(grid_count=("grid_id", "count"), pole_count=("pole_count", "sum"))
        .sort_values("grid_count", ascending=False)
    )

    asos_usage = (
        out.groupby(["nearest_asos_station_id", "nearest_asos_station_name"], as_index=False)
        .agg(grid_count=("grid_id", "count"), pole_count=("pole_count", "sum"))
        .sort_values("grid_count", ascending=False)
    )

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Grid Station Mapping Report\n\n")

        f.write("## 1. Summary\n\n")
        f.write(f"- grid_rows: {len(grid)}\n")
        f.write(f"- station_rows: {len(station)}\n")
        f.write(f"- aws_station_count: {len(aws_st)}\n")
        f.write(f"- asos_station_count: {len(asos_st)}\n")
        f.write(f"- output: {OUT_PATH}\n")
        f.write(f"- output_rows: {len(out)}\n\n")

        f.write("## 2. Distance Summary\n\n")
        f.write(distance_summary.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 3. Top AWS Station Coverage\n\n")
        f.write(aws_usage.head(20).to_markdown(index=False))
        f.write("\n\n")

        f.write("## 4. Top ASOS Station Coverage\n\n")
        f.write(asos_usage.head(20).to_markdown(index=False))
        f.write("\n\n")

        f.write("## 5. Output Columns\n\n")
        for c in out.columns:
            f.write(f"- {c}\n")

    print("Saved:", OUT_PATH)
    print("Saved:", REPORT_PATH)
    print()
    print(out.head())
    print()
    print(distance_summary)


if __name__ == "__main__":
    main()
