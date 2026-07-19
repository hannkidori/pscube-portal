import pandas as pd
import os

to_remove = {
    'megaface_king_scraper': ['2026-07-16'],
    'megaface_myjuggler_scraper': ['2026-07-16'],
    'megaface_newking_scraper': ['2026-07-16'],
    'sunitoman_scraper': ['2026-07-12', '2026-07-14']
}

for folder, dates in to_remove.items():
    csv_path = os.path.join(folder, 'master_data.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        orig_len = len(df)
        df = df[~df['日付'].isin(dates)]
        new_len = len(df)
        if orig_len != new_len:
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"Removed {orig_len - new_len} rows from {csv_path} (Dates: {dates})")
        else:
            print(f"No rows removed from {csv_path} (Dates: {dates})")
