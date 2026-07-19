import pandas as pd
import glob
for f in glob.glob('*_scraper/master_data.csv'):
    df = pd.read_csv(f)
    dates = sorted(df['日付'].unique())
    if len(dates) < 2: continue
    
    for i in range(len(dates)-1):
        d1 = dates[i]
        d2 = dates[i+1]
        df1 = df[df['日付'] == d1].sort_values('台番').reset_index(drop=True)
        df2 = df[df['日付'] == d2].sort_values('台番').reset_index(drop=True)
        
        # Check if BIG回数, REG回数, 累計ゲーム数 are identical
        if len(df1) == len(df2) and len(df1) > 0:
            cols = ['BIG回数', 'REG回数', '累計ゲーム数']
            if (df1[cols] == df2[cols]).all().all():
                print(f"DUPLICATE DATA FOUND in {f}: {d1} and {d2} have exactly identical numbers!")
