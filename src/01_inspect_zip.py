from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "data/raw/contest/contest_data_1.zip"

print("ZIP path:", ZIP_PATH)

if not ZIP_PATH.exists():
    raise FileNotFoundError(f"ZIP file not found: {ZIP_PATH}")

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    names = z.namelist()
    print("Total files:", len(names))
    print()
    for name in names:
        info = z.getinfo(name)
        print(f"{name} | {info.file_size} bytes")
