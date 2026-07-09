import os
import glob
import pandas as pd
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

targets = [
    "megaface_newking_scraper",
    "megaface_king_scraper",
    "sunitoman_newking_scraper"
]

# 1. Update extract_machines.py back to 5-go-ki specs
for folder in targets:
    py_file = os.path.join(base_dir, folder, "extract_machines.py")
    if os.path.exists(py_file):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Update constants at top
        content = re.sub(r'BIG_COINS\s*=\s*260', 'BIG_COINS = 312', content)
        content = re.sub(r'REG_COINS\s*=\s*120', 'REG_COINS = 130', content)
        content = re.sub(r'COIN_PER_GAME\s*=\s*1\.2531', 'COIN_PER_GAME = 1.3513', content)
        
        # Update inline math
        content = re.sub(r'\*\s*260\b', '* 312', content)
        content = re.sub(r'\*\s*120\b', '* 130', content)
        content = re.sub(r'\*\s*1\.2531\b', '* 1.3513', content)
        
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Reverted script in {folder}")

# 2. Update master_data.csv back to original
for folder in targets:
    csv_file = os.path.join(base_dir, folder, "master_data.csv")
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            def calc_diff(row):
                try:
                    games = float(row['累計ゲーム数'])
                    big = float(row['BIG回数'])
                    reg = float(row['REG回数'])
                    return int((big * 312) + (reg * 130) - (games * 1.3513))
                except:
                    return row['推測差枚']
                    
            df['推測差枚'] = df.apply(calc_diff, axis=1)
            
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"Reverted CSV in {folder}")
        except Exception as e:
            print(f"Error reading CSV {csv_file}: {e}")
            
# 3. Update report HTMLs
for folder in targets:
    try:
        import subprocess
        subprocess.run(["python", "generate_html.py"], cwd=os.path.join(base_dir, folder))
    except:
        pass
