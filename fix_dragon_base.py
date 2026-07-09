import os
import re
import pandas as pd
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))
folder = "sunitoman_scraper"

# 1. Update extract_machines.py
py_file = os.path.join(base_dir, folder, "extract_machines.py")
if os.path.exists(py_file):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = re.sub(r'COIN_PER_GAME\s*=\s*50\s*/\s*35\.0.*', 'COIN_PER_GAME = 50 / 39.9  # ベース約39.9G = 約1.2531枚/G', content)
    content = re.sub(r'\*\s*1\.4285\b', '* 1.2531', content)
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Reverted base to 39.9G in {folder}")

# 2. Recalculate CSV
csv_file = os.path.join(base_dir, folder, "master_data.csv")
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    def calc_diff(row):
        try:
            games = float(row['累計ゲーム数'])
            big = float(row['BIG回数'])
            reg = float(row['REG回数'])
            return int((big * 252) + (reg * 96) - (games * 1.2531))
        except:
            return row['推測差枚']
    df['推測差枚'] = df.apply(calc_diff, axis=1)
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"Recalculated CSV with 39.9G in {folder}")

# 3. Regenerate HTML
subprocess.run(["python", "generate_html.py"], cwd=os.path.join(base_dir, folder))
subprocess.run(["python", "update_portal.py"], cwd=base_dir)
