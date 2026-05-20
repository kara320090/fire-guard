from pathlib import Path
import zipfile
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "data" / "raw" / "_inbox"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = REPORT_DIR / "raw_download_inventory.md"
CSV_REPORT_PATH = REPORT_DIR / "raw_download_inventory.csv"

ENCODINGS = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]
SEPARATORS = [",", "\t", "|"]

def try_read_csv(path: Path):
    errors = []
    for enc in ENCODINGS:
        for sep in SEPARATORS:
            try:
                df = pd.read_csv(path, nrows=5, encoding=enc, sep=sep)
                if len(df.columns) >= 2:
                    return {
                        "encoding": enc,
                        "sep": sep,
                        "columns": list(df.columns),
                        "preview": df,
                        "error": None,
                    }
            except Exception as e:
                errors.append(f"{enc}/{sep}: {type(e).__name__}: {e}")
    return {
        "encoding": None,
        "sep": None,
        "columns": [],
        "preview": None,
        "error": " | ".join(errors[:3]),
    }

def inspect_file(path: Path):
    item = {
        "file_name": path.name,
        "relative_path": str(path.relative_to(ROOT)),
        "extension": path.suffix.lower(),
        "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
        "kind": "unknown",
        "encoding": "",
        "sep": "",
        "columns": "",
        "note": "",
    }

    ext = path.suffix.lower()

    if ext == ".csv":
        item["kind"] = "csv"
        result = try_read_csv(path)
        item["encoding"] = result["encoding"] or ""
        item["sep"] = result["sep"] or ""
        item["columns"] = " | ".join(map(str, result["columns"]))
        if result["error"]:
            item["note"] = result["error"]

    elif ext in [".xlsx", ".xls"]:
        item["kind"] = "excel"
        try:
            xls = pd.ExcelFile(path)
            item["columns"] = "sheets: " + " | ".join(xls.sheet_names)
            if xls.sheet_names:
                df = pd.read_excel(path, sheet_name=xls.sheet_names[0], nrows=5)
                item["note"] = "first_sheet_columns: " + " | ".join(map(str, df.columns))
        except Exception as e:
            item["note"] = f"{type(e).__name__}: {e}"

    elif ext == ".zip":
        item["kind"] = "zip"
        try:
            with zipfile.ZipFile(path, "r") as z:
                names = z.namelist()
            item["columns"] = "zip_members: " + " | ".join(names[:20])
            if len(names) > 20:
                item["note"] = f"and {len(names) - 20} more files"
        except Exception as e:
            item["note"] = f"{type(e).__name__}: {e}"

    else:
        item["note"] = "unsupported extension"

    return item

def main():
    if not INBOX.exists():
        raise FileNotFoundError(f"INBOX not found: {INBOX}")

    files = [p for p in INBOX.rglob("*") if p.is_file()]
    files = sorted(files, key=lambda p: p.name.lower())

    rows = [inspect_file(p) for p in files]
    df = pd.DataFrame(rows)
    df.to_csv(CSV_REPORT_PATH, index=False, encoding="utf-8-sig")

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("# Raw Download Inventory\n\n")
        f.write(f"- inbox: {INBOX}\n")
        f.write(f"- file_count: {len(files)}\n\n")

        if df.empty:
            f.write("No files found.\n")
        else:
            f.write("## File Summary\n\n")
            f.write(df.to_markdown(index=False))
            f.write("\n\n")

            f.write("## Next Naming Rule\n\n")
            f.write("- AWS hourly: data/raw/kma_aws/AWS_hourly_gangwon_202503.csv\n")
            f.write("- ASOS hourly: data/raw/kma_asos/ASOS_hourly_gangwon_202503.csv\n")
            f.write("- ASOS daily: data/raw/kma_asos/ASOS_daily_gangwon_202503.csv\n")
            f.write("- Station metadata: data/raw/kma_station_meta/station_meta.csv\n")
            f.write("- Dry warning: data/raw/kma_warning/warning_dry_202503.csv\n")
            f.write("- Strong wind warning: data/raw/kma_warning/warning_strongwind_202503.csv\n")

    print("Saved:", REPORT_PATH)
    print("Saved:", CSV_REPORT_PATH)
    print(df)

if __name__ == "__main__":
    main()
