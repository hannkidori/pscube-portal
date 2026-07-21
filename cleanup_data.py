import os
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
scrapers = [
    'megaface_king_scraper',
    'megaface_newking_scraper',
    'megaface_myjuggler_scraper',
    'sunitoman_scraper',
    'sunitoman_newking_scraper',
    'sunitoman_myjuggler_scraper'
]

cols_to_check = ['BIG回数', 'REG回数', '累計ゲーム数']

for folder in scrapers:
    csv_path = os.path.join(base_dir, folder, 'master_data.csv')
    if not os.path.exists(csv_path):
        continue
        
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    # Normalize daiban (remove leading zeros)
    df['台番'] = df['台番'].astype(int)
    
    dates = sorted(df['日付'].unique())
    dates_to_drop = []
    
    for i in range(1, len(dates)):
        prev_date = dates[i-1]
        curr_date = dates[i]
        
        df_prev = df[df['日付'] == prev_date].sort_values('台番').reset_index(drop=True)
        df_curr = df[df['日付'] == curr_date].sort_values('台番').reset_index(drop=True)
        
        if len(df_prev) == len(df_curr) and len(df_prev) > 0:
            if (df_prev[cols_to_check] == df_curr[cols_to_check]).all().all():
                print(f"[{folder}] Found identical data: {prev_date} == {curr_date}. Dropping {curr_date}")
                dates_to_drop.append(curr_date)
                
    if dates_to_drop:
        df = df[~df['日付'].isin(dates_to_drop)]
        
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"[{folder}] Cleaned up master_data.csv")
