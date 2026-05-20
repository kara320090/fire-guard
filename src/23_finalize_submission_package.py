from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data/outputs/baseline_submission_final_top5.csv"

SUBMISSION_DIR = ROOT / "submission"
FINAL_SUBMISSION_PATH = SUBMISSION_DIR / "FIRE_GUARD_submission_top5.csv"
MANIFEST_PATH = SUBMISSION_DIR / "submission_manifest.md"
REPORT_PATH = ROOT / "reports/final_submission_check_report.md"

REQUIRED_COLUMNS = ["pole_id", "lon", "lat", "decision"]
EXPECTED_ROWS = 1387831


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing input submission: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")

    checks = {}

    checks["input_path"] = str(INPUT_PATH)
    checks["rows"] = len(df)
    checks["expected_rows"] = EXPECTED_ROWS
    checks["row_count_ok"] = len(df) == EXPECTED_ROWS
    checks["columns"] = list(df.columns)
    checks["columns_ok"] = list(df.columns) == REQUIRED_COLUMNS

    checks["pole_id_missing"] = int(df["pole_id"].isna().sum()) if "pole_id" in df.columns else None
    checks["pole_id_duplicates"] = int(df["pole_id"].duplicated().sum()) if "pole_id" in df.columns else None
    checks["lon_missing"] = int(df["lon"].isna().sum()) if "lon" in df.columns else None
    checks["lat_missing"] = int(df["lat"].isna().sum()) if "lat" in df.columns else None

    decision_values = sorted(df["decision"].dropna().unique().tolist()) if "decision" in df.columns else []
    checks["decision_values"] = decision_values
    checks["decision_values_ok"] = set(decision_values).issubset({0, 1})
    checks["decision_1_count"] = int(df["decision"].sum()) if "decision" in df.columns else None
    checks["decision_0_count"] = int((df["decision"] == 0).sum()) if "decision" in df.columns else None
    checks["decision_1_ratio"] = float(df["decision"].mean()) if "decision" in df.columns else None

    checks["lon_min"] = float(df["lon"].min())
    checks["lon_max"] = float(df["lon"].max())
    checks["lat_min"] = float(df["lat"].min())
    checks["lat_max"] = float(df["lat"].max())

    hard_fail = []
    if not checks["row_count_ok"]:
        hard_fail.append("row_count_not_expected")
    if not checks["columns_ok"]:
        hard_fail.append("columns_not_official_format")
    if checks["pole_id_duplicates"] != 0:
        hard_fail.append("pole_id_duplicates")
    if checks["lon_missing"] != 0 or checks["lat_missing"] != 0:
        hard_fail.append("coordinate_missing")
    if not checks["decision_values_ok"]:
        hard_fail.append("decision_values_not_binary")

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 최종 제출 파일 복사
    df.to_csv(FINAL_SUBMISSION_PATH, index=False, encoding="utf-8-sig")

    file_size_mb = FINAL_SUBMISSION_PATH.stat().st_size / (1024 * 1024)
    file_hash = sha256_file(FINAL_SUBMISSION_PATH)

    checks["final_submission_path"] = str(FINAL_SUBMISSION_PATH)
    checks["final_file_size_mb"] = round(file_size_mb, 3)
    checks["sha256"] = file_hash
    checks["hard_fail_count"] = len(hard_fail)
    checks["hard_fail"] = hard_fail

    check_df = pd.DataFrame([
        {"item": k, "value": str(v)}
        for k, v in checks.items()
    ])

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Final Submission Check Report\n\n")
        f.write("## 1. Validation Result\n\n")
        f.write(check_df.to_markdown(index=False))
        f.write("\n\n")

        f.write("## 2. Final Judgment\n\n")
        if len(hard_fail) == 0:
            f.write("- PASS: final submission file passed structural validation.\n")
        else:
            f.write("- FAIL: final submission file has hard validation issues.\n")
            for item in hard_fail:
                f.write(f"  - {item}\n")

    with open(MANIFEST_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# FIRE-GUARD Submission Manifest\n\n")
        f.write(f"- final_submission_file: {FINAL_SUBMISSION_PATH.relative_to(ROOT)}\n")
        f.write(f"- rows: {checks['rows']}\n")
        f.write(f"- columns: {REQUIRED_COLUMNS}\n")
        f.write(f"- decision_1_count: {checks['decision_1_count']}\n")
        f.write(f"- decision_0_count: {checks['decision_0_count']}\n")
        f.write(f"- decision_1_ratio: {checks['decision_1_ratio']}\n")
        f.write(f"- file_size_mb: {checks['final_file_size_mb']}\n")
        f.write(f"- sha256: {file_hash}\n")
        f.write("\n## Notes\n\n")
        f.write("- This file is generated from data/outputs/baseline_submission_final_top5.csv.\n")
        f.write("- This is the selected top5 rule-based baseline submission.\n")
        f.write("- Do not edit the CSV manually after hash generation.\n")

    print("Saved:", FINAL_SUBMISSION_PATH)
    print("Saved:", MANIFEST_PATH)
    print("Saved:", REPORT_PATH)
    print()
    print(check_df)

    if hard_fail:
        raise RuntimeError(f"Final submission validation failed: {hard_fail}")


if __name__ == "__main__":
    main()
