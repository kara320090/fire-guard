from pathlib import Path
import pandas as pd

IN_PATH = Path("data/raw/kma_warning/warning_dry_strongwind_202503.csv")
OUT_PATH = Path("data/raw/kma_warning/warning_dry_strongwind_202503_utf8.csv")

for enc in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
    try:
        df = pd.read_csv(IN_PATH, encoding=enc)
        print("Read success:", enc)
        print(df.head())
        print(df.columns)
        df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
        print("Saved:", OUT_PATH)
        break
    except Exception as e:
        print("Failed:", enc, e)
