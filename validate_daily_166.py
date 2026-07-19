import os
import pandas as pd
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
folders = {
    'megaface_newking_scraper': 54,
    'megaface_king_scraper': 18,
    'megaface_myjuggler_scraper': 22,
    'sunitoman_scraper': 30,
    'sunitoman_newking_scraper': 30,
    'sunitoman_myjuggler_scraper': 12
}

store_names = {
    'megaface_newking_scraper': 'メガフェイス豊崎(ニューキング)',
    'megaface_king_scraper': 'メガフェイス豊崎(キングハナハナ)',
    'megaface_myjuggler_scraper': 'メガフェイス豊崎(マイジャグラー)',
    'sunitoman_scraper': 'サンシャイン糸満(ドラゴンハナハナ)',
    'sunitoman_newking_scraper': 'サンシャイン糸満(ニューキング)',
    'sunitoman_myjuggler_scraper': 'サンシャイン糸満(マイジャグラー)'
}

all_dfs = []
for folder in folders:
    csv_path = os.path.join(base_dir, folder, 'master_data.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        if not df.empty:
            df['folder'] = folder
            all_dfs.append(df)

if not all_dfs:
    print("データがありません。")
    sys.exit(0)

combined_df = pd.concat(all_dfs)
latest_date = combined_df['日付'].max()

print(f"[{latest_date}] のデータ完全性をチェックしています...")

latest_data = combined_df[combined_df['日付'] == latest_date]
counts = latest_data.groupby('folder').size()

total = 0
errors = []
for folder, expected in folders.items():
    actual = counts.get(folder, 0)
    total += actual
    if actual != expected:
        errors.append(f"[エラー] {store_names[folder]} : 取得 {actual}台 / 想定 {expected}台")
    else:
        print(f"[OK] {store_names[folder]} : {actual}台")

if total != 166:
    print("\n===================================================")
    print("       [エラー]: 166台すべて揃っていません ")
    print("===================================================\n")
    for e in errors:
        print(e)
    print(f"\n合計取得台数: {total}台 (不足: {166 - total}台)")
    print("更新を中断します。不足しているHTMLファイルを追加してから再度実行してください。")
    sys.exit(1)

print("\n===================================================")
print("      [OK] 2店舗6機種166台 すべて揃っています ")
print("===================================================\n")
sys.exit(0)
