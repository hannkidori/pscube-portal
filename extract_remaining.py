import os
import shutil
import subprocess
import glob

folders = ['20260722', '20260723']
for folder in folders:
    for f in glob.glob(f'daily_import/{folder}/*.html'):
        if '1' in f or 'マイジャグラー' in f:
            dest_folder = 'sunitoman_myjuggler_scraper'
        elif '2' in f or 'ニューキング' in f:
            dest_folder = 'sunitoman_newking_scraper'
        elif '3' in f or 'ドラゴン' in f:
            dest_folder = 'sunitoman_scraper'
        else:
            continue
            
        filename = os.path.basename(f)
        dest_path = os.path.join(dest_folder, filename)
        
        shutil.copy2(f, dest_path)
        print(f"Copied {f} to {dest_path}")
        subprocess.run(["python", "extract_machines.py"], cwd=dest_folder, check=True)
        os.remove(dest_path)
        print(f"Processed and deleted {dest_path}")
