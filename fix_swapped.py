import pandas as pd
import shutil
import subprocess
import os

# 1. Clean the 21st data from both CSVs
for py_file in ['sunitoman_newking_scraper/master_data.csv', 'sunitoman_scraper/master_data.csv']:
    df = pd.read_csv(py_file, encoding='utf-8-sig')
    orig = len(df)
    df = df[df['日付'] != '2026-07-21']
    df.to_csv(py_file, index=False, encoding='utf-8-sig')
    print(f'Cleaned 21st from {py_file} ({orig} -> {len(df)})')

# 2. Extract 21st data but SWAPPED!
# 3.html is New King, 2.html is Dragon
tasks = [
    ("daily_import_archive/3.html", "sunitoman_newking_scraper", "3.html"),
    ("daily_import_archive/2.html", "sunitoman_scraper", "2.html")
]

for src, folder, dest_name in tasks:
    if os.path.exists(src):
        dest_path = os.path.join(folder, dest_name)
        shutil.copy2(src, dest_path)
        print(f"Copied {src} to {dest_path}")
        subprocess.run(["python", "extract_machines.py"], cwd=folder, check=True)
        os.remove(dest_path)
        print(f"Processed and deleted {dest_path}")
