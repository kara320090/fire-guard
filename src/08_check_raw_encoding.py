from pathlib import Path
import pandas as pd

files = list(Path("data/raw").rglob("*.csv"))

for p in files:
    print("\nFILE:", p)
    for enc in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(p, nrows=3, encoding=enc)
            print("  OK encoding:", enc)
            print("  columns:", list(df.columns))
            print(df.head(1))
            break
        except Exception as e:
            print("  fail:", enc, type(e).__name__)
