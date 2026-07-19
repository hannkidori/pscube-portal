import pandas as pd
import glob
import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
scrapers = [
    'megaface_king_scraper',
    'megaface_myjuggler_scraper',
    'megaface_newking_scraper',
    'sunitoman_scraper',
    'sunitoman_newking_scraper',
    'sunitoman_myjuggler_scraper'
]

errors = []

for folder in scrapers:
    csv_path = os.path.join(base_dir, folder, 'master_data.csv')
    if not os.path.exists(csv_path):
        continue
        
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    dates = sorted(df['日付'].unique())
    
    if len(dates) < 2:
        continue
        
    # 最新の日付とその前の日付を比較
    latest_date = dates[-1]
    prev_date = dates[-2]
    
    df_latest = df[df['日付'] == latest_date].sort_values('台番').reset_index(drop=True)
    df_prev = df[df['日付'] == prev_date].sort_values('台番').reset_index(drop=True)
    
    if len(df_latest) == len(df_prev) and len(df_latest) > 0:
        cols = ['BIG回数', 'REG回数', '累計ゲーム数']
        # 全ての台でBIG・REG・ゲーム数が一致するかチェック
        if (df_latest[cols] == df_prev[cols]).all().all():
            errors.append(f"[{folder}] {prev_date} と {latest_date} のデータが完全に同一です。")

if errors:
    print("\n===================================================")
    print("       [エラー]: 重複データ（前日のコピー）を検知しました ")
    print("===================================================\n")
    for e in errors:
        print(e)
    print("\nデータの更新が遅れているか、誤った日付のタブで保存されています。")
    print("ポータルへの反映を中断します。正しいデータを再取得してください。")
    sys.exit(1)
else:
    print("      [OK] 重複データ（前日のコピー）はありません ")
    sys.exit(0)
