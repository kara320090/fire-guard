from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

GRID_PATH = ROOT / "data" / "interim" / "grid_1km_active.parquet"
OUT_DIR = ROOT / "data" / "outputs"
REPORT_DIR = ROOT / "reports"

OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TOP_N = 100

def main():
    if not GRID_PATH.exists():
        raise FileNotFoundError(f"Missing grid file: {GRID_PATH}")

    grid = pd.read_parquet(GRID_PATH)

    print("Grid shape:", grid.shape)

    summary = grid["pole_count"].describe(
        percentiles=[0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    ).reset_index()
    summary.columns = ["metric", "pole_count"]

    density_summary_path = OUT_DIR / "grid_density_summary.csv"
    summary.to_csv(density_summary_path, index=False, encoding="utf-8-sig")

    top = grid.sort_values("pole_count", ascending=False).head(TOP_N).copy()
    top_cols = [
        "grid_id",
        "pole_count",
        "pole_density",
        "center_lon",
        "center_lat",
        "sw_lon",
        "sw_lat",
        "ne_lon",
        "ne_lat",
    ]
    top_path = OUT_DIR / f"top_dense_grids_{TOP_N}.csv"
    top[top_cols].to_csv(top_path, index=False, encoding="utf-8-sig")

    report_path = REPORT_DIR / "grid_density_summary.md"
    with open(report_path, "w", encoding="utf-8-sig") as f:
        f.write("# Grid Density Summary\n\n")

        f.write("## 1. Summary\n\n")
        f.write(f"- active_grid_count: {len(grid)}\n")
        f.write(f"- total_poles: {int(grid['pole_count'].sum())}\n")
        f.write(f"- mean_poles_per_grid: {float(grid['pole_count'].mean()):.2f}\n")
        f.write(f"- median_poles_per_grid: {float(grid['pole_count'].median()):.2f}\n")
        f.write(f"- max_poles_per_grid: {int(grid['pole_count'].max())}\n\n")

        f.write("## 2. Pole Count Distribution\n\n")
        f.write(summary.to_markdown(index=False))
        f.write("\n\n")

        f.write(f"## 3. Top {TOP_N} Dense Grids\n\n")
        f.write(top[top_cols].head(20).to_markdown(index=False))
        f.write("\n\n")

        f.write("## 4. Output Files\n\n")
        f.write(f"- {density_summary_path}\n")
        f.write(f"- {top_path}\n")

    print("Saved:", density_summary_path)
    print("Saved:", top_path)
    print("Saved:", report_path)

if __name__ == "__main__":
    main()
