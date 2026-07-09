import os
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
folders = [
    'megaface_newking_scraper', 'megaface_king_scraper', 'megaface_myjuggler_scraper',
    'sunitoman_scraper', 'sunitoman_newking_scraper', 'sunitoman_myjuggler_scraper'
]

store_names = {
    'megaface_newking_scraper': 'メガフェイス豊崎 (ニューキング)',
    'megaface_king_scraper': 'メガフェイス豊崎 (キングハナハナ)',
    'megaface_myjuggler_scraper': 'メガフェイス豊崎 (マイジャグラー)',
    'sunitoman_scraper': 'サンシャイン糸満 (ドラゴンハナハナ)',
    'sunitoman_newking_scraper': 'サンシャイン糸満 (ニューキング)',
    'sunitoman_myjuggler_scraper': 'サンシャイン糸満 (マイジャグラー)'
}

alerts = []
all_dfs = []
valid_folders = []
for folder in folders:
    csv_path = os.path.join(base_dir, folder, 'master_data.csv')
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            if not df.empty:
                df['日付'] = pd.to_datetime(df['日付'])
                all_dfs.append((folder, df))
                valid_folders.append(folder)
        except Exception as e:
            alerts.append(f"[{store_names[folder]}] CSVの読み込みに失敗しました: {e}")

if not all_dfs:
    print("データがありません。")
    exit()

global_max_date = pd.concat([df for _, df in all_dfs])['日付'].max()

for folder, df in all_dfs:
    dates = sorted(df['日付'].unique())
    if not dates:
        continue
        
    start_date = dates[0]
    
    # 1. Check for missing dates in the sequence up to global_max_date
    expected_dates = pd.date_range(start=start_date, end=global_max_date)
    missing_dates = expected_dates.difference(dates)

    
    for md in missing_dates:
        alerts.append(f"[日抜け] {store_names[folder]} : {md.strftime('%Y-%m-%d')} のデータが丸ごと抜けています！")
        
    # 2. Check for missing machines (compare to max machines seen)
    counts = df.groupby('日付').size()
    max_count = counts.max()
    
    for date, count in counts.items():
        if count < max_count:
            alerts.append(f"[台数不足] {store_names[folder]} : {date.strftime('%Y-%m-%d')} (取得: {count}台 / 想定: {max_count}台) - HTMLページが一部保存されていない可能性があります。")

print("\n===================================================")
print("             【データ抜けチェック結果】")
print("===================================================\n")

if alerts:
    for a in alerts:
        print(a)
    print("\n※上記のアラートが出た場合、該当する日のファイルを保存し直して再度取り込んでください。")
else:
    print("データの抜けは見つかりませんでした！完璧です！")

print("\n===================================================\n")
