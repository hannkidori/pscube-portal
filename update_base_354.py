import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

targets = [
    "megaface_newking_scraper",
    "sunitoman_newking_scraper"
]

for folder in targets:
    py_file = os.path.join(base_dir, folder, "extract_machines.py")
    if os.path.exists(py_file):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Update constants at top
        content = re.sub(r'COIN_PER_GAME\s*=\s*1\.3513', 'COIN_PER_GAME = 1.4124', content)
        content = re.sub(r'約37\.0G', '約35.4G (取りこぼし考慮の実ベース)', content)
        content = re.sub(r'1\.3513枚/G', '1.4124枚/G', content)
        
        # Update inline math
        content = re.sub(r'\*\s*1\.3513\b', '* 1.4124', content)
        
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated base to 35.4G in {folder}")

# Recalculate CSVs
import pandas as pd
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
                    return int((big * 312) + (reg * 130) - (games * 1.4124))
                except:
                    return row['推測差枚']
            df['推測差枚'] = df.apply(calc_diff, axis=1)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"Recalculated CSV with 35.4G in {folder}")
        except Exception as e:
            print(f"Error reading CSV {csv_file}: {e}")

# Regenerate HTML
import subprocess
for folder in targets:
    try:
        subprocess.run(["python", "generate_html.py"], cwd=os.path.join(base_dir, folder))
    except:
        pass
