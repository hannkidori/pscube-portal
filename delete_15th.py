import pandas as pd
import glob

for f in glob.glob('megaface_*_scraper/master_data.csv'):
    df = pd.read_csv(f, encoding='utf-8-sig')
    original_len = len(df)
    df = df[df['日付'] != '2026-07-15']
    new_len = len(df)
    if original_len != new_len:
        df.to_csv(f, index=False, encoding='utf-8-sig')
        print(f"Deleted {original_len - new_len} rows of 15th data from {f}")
    else:
        print(f"No 15th data found in {f}")
