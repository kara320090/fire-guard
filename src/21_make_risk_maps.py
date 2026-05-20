from pathlib import Path
import pandas as pd
import folium
import branca.colormap as cm

ROOT = Path(__file__).resolve().parents[1]

GRID_SUMMARY_PATH = ROOT / "data/features/grid_risk_summary_202503.parquet"
GRID_SHAPE_PATH = ROOT / "data/interim/grid_1km_active.parquet"
POLE_RISK_PATH = ROOT / "data/features/pole_risk_scores_202503.parquet"

OUT_DIR = ROOT / "data/outputs"
GRID_MAP_PATH = OUT_DIR / "risk_map_grid_top5000.html"
POLE_MAP_PATH = OUT_DIR / "risk_map_top_poles_500.html"
TOP_GRID_CSV_PATH = OUT_DIR / "top_risk_grids_500.csv"
REPORT_PATH = ROOT / "reports/risk_map_report.md"


def load_data():
    if not GRID_SUMMARY_PATH.exists():
        raise FileNotFoundError(f"Missing grid risk summary: {GRID_SUMMARY_PATH}")

    if not GRID_SHAPE_PATH.exists():
        raise FileNotFoundError(f"Missing grid shape file: {GRID_SHAPE_PATH}")

    if not POLE_RISK_PATH.exists():
        raise FileNotFoundError(f"Missing pole risk file: {POLE_RISK_PATH}")

    grid_risk = pd.read_parquet(GRID_SUMMARY_PATH)
    grid_shape = pd.read_parquet(GRID_SHAPE_PATH)
    pole_risk = pd.read_parquet(POLE_RISK_PATH)

    return grid_risk, grid_shape, pole_risk


def make_grid_map(grid_risk: pd.DataFrame, grid_shape: pd.DataFrame):
    required_shape_cols = ["grid_id", "sw_lon", "sw_lat", "ne_lon", "ne_lat"]
    missing = [c for c in required_shape_cols if c not in grid_shape.columns]
    if missing:
        raise ValueError(f"grid_shape missing columns: {missing}")

    required_risk_cols = [
        "grid_id",
        "grid_final_risk_score_100",
        "grid_final_risk_grade",
        "pole_count",
        "risk_max",
        "risk_p95",
        "high_day_count",
        "peak_date",
        "peak_grid_risk_score_100",
        "peak_temp_max",
        "peak_humidity_min",
        "peak_wind_max",
        "peak_no_rain_days",
    ]
    missing = [c for c in required_risk_cols if c not in grid_risk.columns]
    if missing:
        raise ValueError(f"grid_risk missing columns: {missing}")

    merged = grid_risk.merge(
        grid_shape[required_shape_cols],
        on="grid_id",
        how="left",
    )

    merged = merged.dropna(subset=["sw_lon", "sw_lat", "ne_lon", "ne_lat"]).copy()
    merged = merged.sort_values("grid_final_risk_score_100", ascending=False).reset_index(drop=True)

    top500 = merged.head(500).copy()
    top500.to_csv(TOP_GRID_CSV_PATH, index=False, encoding="utf-8-sig")

    # 지도 과부하 방지를 위해 상위 5000개 grid만 그림
    draw = merged.head(5000).copy()

    center_lat = float(draw["center_lat"].mean()) if "center_lat" in draw.columns else float((draw["sw_lat"].mean() + draw["ne_lat"].mean()) / 2)
    center_lon = float(draw["center_lon"].mean()) if "center_lon" in draw.columns else float((draw["sw_lon"].mean() + draw["ne_lon"].mean()) / 2)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB positron")

    min_score = float(draw["grid_final_risk_score_100"].min())
    max_score = float(draw["grid_final_risk_score_100"].max())

    colormap = cm.linear.YlOrRd_09.scale(min_score, max_score)
    colormap.caption = "Grid final risk score"

    for _, r in draw.iterrows():
        score = float(r["grid_final_risk_score_100"])
        color = colormap(score)

        popup = folium.Popup(
            html=f"""
            <b>grid_id</b>: {r['grid_id']}<br>
            <b>risk_score</b>: {score:.3f}<br>
            <b>grade</b>: {r['grid_final_risk_grade']}<br>
            <b>pole_count</b>: {int(r['pole_count'])}<br>
            <b>risk_max</b>: {float(r['risk_max']):.3f}<br>
            <b>risk_p95</b>: {float(r['risk_p95']):.3f}<br>
            <b>high_day_count</b>: {int(r['high_day_count'])}<br>
            <b>peak_date</b>: {r['peak_date']}<br>
            <b>peak_score</b>: {float(r['peak_grid_risk_score_100']):.3f}<br>
            <b>peak_temp_max</b>: {float(r['peak_temp_max']):.3f}<br>
            <b>peak_humidity_min</b>: {float(r['peak_humidity_min']):.3f}<br>
            <b>peak_wind_max</b>: {float(r['peak_wind_max']):.3f}<br>
            <b>peak_no_rain_days</b>: {float(r['peak_no_rain_days']):.3f}<br>
            """,
            max_width=420,
        )

        folium.Rectangle(
            bounds=[
                [float(r["sw_lat"]), float(r["sw_lon"])],
                [float(r["ne_lat"]), float(r["ne_lon"])],
            ],
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.55,
            weight=0.4,
            popup=popup,
        ).add_to(m)

    colormap.add_to(m)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    m.save(GRID_MAP_PATH)

    return {
        "grid_total": len(merged),
        "grid_drawn": len(draw),
        "top_grid_csv": str(TOP_GRID_CSV_PATH.relative_to(ROOT)),
        "grid_map": str(GRID_MAP_PATH.relative_to(ROOT)),
        "risk_min": min_score,
        "risk_max": max_score,
    }


def make_pole_map(pole_risk: pd.DataFrame):
    required_cols = [
        "pole_id",
        "lon",
        "lat",
        "grid_id",
        "pole_risk_score_100",
        "grid_final_risk_grade",
        "risk_max",
        "risk_p95",
        "high_day_count",
        "peak_date",
        "peak_temp_max",
        "peak_humidity_min",
        "peak_wind_max",
        "peak_no_rain_days",
    ]

    missing = [c for c in required_cols if c not in pole_risk.columns]
    if missing:
        raise ValueError(f"pole_risk missing columns: {missing}")

    draw = pole_risk.sort_values("pole_risk_score_100", ascending=False).head(500).copy()

    center_lat = float(draw["lat"].mean())
    center_lon = float(draw["lon"].mean())

    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB positron")

    min_score = float(draw["pole_risk_score_100"].min())
    max_score = float(draw["pole_risk_score_100"].max())

    colormap = cm.linear.YlOrRd_09.scale(min_score, max_score)
    colormap.caption = "Pole risk score"

    for _, r in draw.iterrows():
        score = float(r["pole_risk_score_100"])
        color = colormap(score)

        popup = folium.Popup(
            html=f"""
            <b>pole_id</b>: {r['pole_id']}<br>
            <b>grid_id</b>: {r['grid_id']}<br>
            <b>risk_score</b>: {score:.3f}<br>
            <b>grade</b>: {r['grid_final_risk_grade']}<br>
            <b>risk_max</b>: {float(r['risk_max']):.3f}<br>
            <b>risk_p95</b>: {float(r['risk_p95']):.3f}<br>
            <b>high_day_count</b>: {int(r['high_day_count'])}<br>
            <b>peak_date</b>: {r['peak_date']}<br>
            <b>peak_temp_max</b>: {float(r['peak_temp_max']):.3f}<br>
            <b>peak_humidity_min</b>: {float(r['peak_humidity_min']):.3f}<br>
            <b>peak_wind_max</b>: {float(r['peak_wind_max']):.3f}<br>
            <b>peak_no_rain_days</b>: {float(r['peak_no_rain_days']):.3f}<br>
            """,
            max_width=420,
        )

        folium.CircleMarker(
            location=[float(r["lat"]), float(r["lon"])],
            radius=4,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=0.5,
            popup=popup,
        ).add_to(m)

    colormap.add_to(m)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    m.save(POLE_MAP_PATH)

    return {
        "pole_total": len(pole_risk),
        "pole_drawn": len(draw),
        "pole_map": str(POLE_MAP_PATH.relative_to(ROOT)),
        "risk_min": min_score,
        "risk_max": max_score,
    }


def main():
    grid_risk, grid_shape, pole_risk = load_data()

    print("grid_risk:", grid_risk.shape)
    print("grid_shape:", grid_shape.shape)
    print("pole_risk:", pole_risk.shape)

    grid_result = make_grid_map(grid_risk, grid_shape)
    pole_result = make_pole_map(pole_risk)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Risk Map Report\n\n")

        f.write("## 1. Grid Risk Map\n\n")
        for k, v in grid_result.items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## 2. Top Pole Risk Map\n\n")
        for k, v in pole_result.items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## 3. Notes\n\n")
        f.write("- Grid map draws top 5000 grid cells by final risk score to avoid excessive HTML size.\n")
        f.write("- Pole map draws top 500 poles by pole risk score.\n")
        f.write("- These maps are for reporting and qualitative evaluation, not official submission format.\n")

    print("Saved:", GRID_MAP_PATH)
    print("Saved:", POLE_MAP_PATH)
    print("Saved:", TOP_GRID_CSV_PATH)
    print("Saved:", REPORT_PATH)


if __name__ == "__main__":
    main()
