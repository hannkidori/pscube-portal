import pandas as pd
import glob

for f in glob.glob('sunitoman*scraper/master_data.csv'):
    df = pd.read_csv(f, encoding='utf-8-sig')
    original_len = len(df)
    df = df[~df['日付'].isin(['2026-07-21', '2026-07-22', '2026-07-23'])]
    df.to_csv(f, index=False, encoding='utf-8-sig')
    print(f'Cleaned {f}, removed {original_len - len(df)} records')
