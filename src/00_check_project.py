from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required_paths = [
    "data/raw/contest/contest_data_1.zip",
    "data/raw/kma_aws",
    "data/raw/kma_asos",
    "data/raw/kma_station_meta",
    "data/raw/kma_warning",
    "data/interim",
    "data/features",
    "data/outputs",
    "notebooks",
    "src",
    "app",
    "reports",
    "reports/figures",
    "README.md",
    "requirements.txt",
    "reports/data_source_table.csv",
    "reports/data_inventory.md",
]

print("FIRE-GUARD project check")
print("ROOT:", ROOT)
print()

ok = True

for rel in required_paths:
    path = ROOT / rel
    exists = path.exists()
    status = "OK" if exists else "MISSING"
    print(f"{status:8} {rel}")
    if not exists:
        ok = False

print()
if ok:
    print("Project structure is ready.")
else:
    print("Some files or folders are missing.")
