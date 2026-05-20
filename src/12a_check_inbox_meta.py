from pathlib import Path
import pandas as pd

files = list(Path("data/raw/_inbox").glob("META*.csv"))

print("META files:", len(files))

for p in files:
    print("\nFILE:", p)
    for enc in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            df = pd.read_csv(p, encoding=enc)
            print("encoding:", enc)
            print("shape:", df.shape)
            print("columns:", list(df.columns))
            print(df.head(5))
            break
        except Exception as e:
            print("fail:", enc, type(e).__name__)
