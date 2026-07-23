import pandas as pd
import glob

for py_file in glob.glob('sunitoman*scraper/master_data.csv'):
    df = pd.read_csv(py_file, encoding='utf-8-sig')
    orig = len(df)
    df = df[~df['日付'].isin(['2026-07-22', '2026-07-23'])]
    df.to_csv(py_file, index=False, encoding='utf-8-sig')
    print(f'Cleaned {py_file} from {orig} to {len(df)}')
