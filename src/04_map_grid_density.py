from pathlib import Path
import pandas as pd
import folium
import branca.colormap as cm

ROOT = Path(__file__).resolve().parents[1]

GRID_PATH = ROOT / "data" / "interim" / "grid_1km_active.parquet"
OUT_PATH = ROOT / "data" / "outputs" / "grid_pole_density_map.html"

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

MAX_CELLS_TO_DRAW = 5000


def main():
    if not GRID_PATH.exists():
        raise FileNotFoundError(f"Missing grid file: {GRID_PATH}")

    grid = pd.read_parquet(GRID_PATH)

    print("Grid shape:", grid.shape)

    # HTML이 너무 무거워지는 것을 막기 위해 밀도 상위 grid 중심으로 표시
    draw = grid.sort_values("pole_count", ascending=False).head(MAX_CELLS_TO_DRAW).copy()

    center_lat = draw["center_lat"].mean()
    center_lon = draw["center_lon"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles="cartodbpositron",
    )

    max_value = draw["pole_density"].quantile(0.99)
    if max_value <= 0:
        max_value = draw["pole_density"].max()

    colormap = cm.linear.YlOrRd_09.scale(0, max_value)
    colormap.caption = "Pole density per km²"

    for _, row in draw.iterrows():
        value = float(row["pole_density"])
        clipped = min(value, max_value)
        color = colormap(clipped)

        bounds = [
            [float(row["sw_lat"]), float(row["sw_lon"])],
            [float(row["ne_lat"]), float(row["ne_lon"])],
        ]

        popup = (
            f"grid_id: {row['grid_id']}<br>"
            f"pole_count: {int(row['pole_count'])}<br>"
            f"pole_density: {float(row['pole_density']):.2f}"
        )

        folium.Rectangle(
            bounds=bounds,
            color="gray",
            weight=0.2,
            fill=True,
            fill_color=color,
            fill_opacity=0.65,
            popup=popup,
        ).add_to(m)

    colormap.add_to(m)

    folium.LayerControl().add_to(m)

    m.save(OUT_PATH)
    print("Saved map:", OUT_PATH)
    print("Drawn cells:", len(draw))


if __name__ == "__main__":
    main()
