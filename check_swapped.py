import pandas as pd

for file, name in [('sunitoman_newking_scraper/master_data.csv', 'New King'), ('sunitoman_scraper/master_data.csv', 'Dragon')]:
    df = pd.read_csv(file, encoding='utf-8-sig')
    print(f"--- {name} ---")
    for date in ['2026-07-20', '2026-07-21', '2026-07-22', '2026-07-23']:
        df_date = df[df['日付'] == date]
        if len(df_date) > 0:
            print(f"{date}:", df_date['台番'].tolist()[:3])
        else:
            print(f"{date}: Missing")
