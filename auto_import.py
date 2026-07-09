import os
import glob
import shutil
import subprocess
import uuid

base_dir = os.path.dirname(os.path.abspath(__file__))
import_dir = os.path.join(base_dir, "daily_import")

# ターゲットフォルダのマッピング
targets = {
    "MEGAFACE_NEWKING": "megaface_newking_scraper",
    "MEGAFACE_KING": "megaface_king_scraper",
    "MEGAFACE_MYJUGGLER": "megaface_myjuggler_scraper",
    "SUNITOMAN_DRAGON": "sunitoman_scraper",
    "SUNITOMAN_NEWKING": "sunitoman_newking_scraper",
    "SUNITOMAN_MYJUGGLER": "sunitoman_myjuggler_scraper"
}

all_scraper_folders = list(targets.values())
updated_folders = set()

def identify_file(filepath):
    # ファイルの先頭数KBを読んで判定する
    content = ""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(20000)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None
        
    store = None
    if "メガフェイス" in content or "MEGA FACE" in content.upper():
        store = "MEGAFACE"
    elif "サンシャイン" in content or "SUNSHINE" in content.upper() or "premot.co.jp" in content:
        # P-moba uses premot.co.jp, usually it says サンシャイン
        store = "SUNITOMAN"
        
    machine = None
    # 機種名の判定 (半角カタカナにも対応)
    if "ニューキング" in content or "ﾆｭｰｷﾝｸﾞ" in content:
        machine = "NEWKING"
    elif "ドラゴンハナハナ" in content or "ﾄﾞﾗｺﾞﾝ" in content:
        machine = "DRAGON"
    elif "キングハナハナ" in content or "ｷﾝｸﾞﾊﾅﾊﾅ" in content:
        machine = "KING"
    elif "マイジャグラー" in content or "ﾏｲｼﾞｬｸﾞﾗｰ" in content:
        machine = "MYJUGGLER"
        
    if store and machine:
        key = f"{store}_{machine}"
        if key in targets:
            return targets[key]
            
    return None

def main():
    if not os.path.exists(import_dir):
        print(f"Error: {import_dir} が存在しません。")
        return
        
    # daily_import内のすべてのhtml/mhtファイルを再帰的に検索
    search_pattern = os.path.join(import_dir, "**", "*.*")
    files = glob.glob(search_pattern, recursive=True)
    html_files = [f for f in files if f.lower().endswith(('.html', '.htm', '.mht'))]
    
    if not html_files:
        print("処理するHTMLファイルが見つかりません。")
        return
        
    print(f"合計 {len(html_files)} 件のファイルを処理します...")
    
    temp_files_to_delete = []
    
    # 1. 各ファイルを判別して一時コピー
    for f in html_files:
        target_folder = identify_file(f)
        if target_folder:
            print(f"[OK] {os.path.basename(f)} -> {target_folder}")
            # ユニークな名前で一時コピー
            tmp_name = f"auto_import_{uuid.uuid4().hex[:8]}.html"
            dest_path = os.path.join(base_dir, target_folder, tmp_name)
            shutil.copy2(f, dest_path)
            temp_files_to_delete.append(dest_path)
            updated_folders.add(target_folder)
        else:
            print(f"[?] {os.path.basename(f)} -> 判別不能のためスキップ")
            
    # 2. 更新があったフォルダの抽出スクリプトを実行
    for folder in updated_folders:
        print(f"\n[{folder}] データを抽出中...")
        folder_path = os.path.join(base_dir, folder)
        try:
            subprocess.run(['python', 'extract_machines.py'], cwd=folder_path, check=True)
        except Exception as e:
            print(f"Error running extract_machines.py in {folder}: {e}")
            
    # 3. 一時コピーしたファイルを削除
    for tmp_file in temp_files_to_delete:
        try:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        except Exception as e:
            print(f"Could not delete temp file {tmp_file}: {e}")
            
    print("\nデータの重複をチェック・自動修正中...")
    for folder in all_scraper_folders:
        csv_path = os.path.join(base_dir, folder, "master_data.csv")
        if os.path.exists(csv_path):
            try:
                import pandas as pd
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                if not df.empty:
                    orig_len = len(df)
                    df = df.drop_duplicates(subset=['日付', '台番'], keep='last')
                    if len(df) != orig_len:
                        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                        print(f"[{folder}] 重複データを {orig_len - len(df)} 件削除しました。")
            except Exception as e:
                print(f"[{folder}] 重複チェックエラー: {e}")

    print("\n異常データの自動検知を実行中...")
    try:
        subprocess.run(['python', 'check_anomalies.py'], cwd=base_dir, check=True)
    except Exception as e:
        print(f"Error running check_anomalies.py: {e}")

    print("\n全レポートとポータルページを更新中...")
    import pandas as pd
    for folder in all_scraper_folders:
        folder_path = os.path.join(base_dir, folder)
        csv_path = os.path.join(folder_path, "master_data.csv")
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                dates = df['日付'].dropna().unique()
                for d in dates:
                    subprocess.run(['python', 'generate_html.py', str(d)], cwd=folder_path, check=True)
            # 最後に引数なしで実行し、最新のreport.htmlを生成
            subprocess.run(['python', 'generate_html.py'], cwd=folder_path, check=True)
        except Exception as e:
            print(f"Error running generate_html.py in {folder}: {e}")
            
    print("\n狙い目の結果検証を実行中...")
    try:
        subprocess.run(['python', 'validate_predictions.py'], cwd=base_dir, check=True)
    except Exception as e:
        print(f"Error running validate_predictions.py: {e}")

    # update_portal.py is now called explicitly to ensure anomalies are injected
    try:
        subprocess.run(['python', 'update_portal.py'], cwd=base_dir, check=True)
    except Exception as e:
        print(f"Error running update_portal.py: {e}")
            
    print("\n[OK] データ抜けチェックを実行中...")
    try:
        subprocess.run(['python', 'check_missing_data.py'], cwd=base_dir, check=True)
    except Exception as e:
        print(f"Error running check_missing_data.py: {e}")

    print("\n[OK] すべての処理が完了しました！")

if __name__ == "__main__":
    main()
