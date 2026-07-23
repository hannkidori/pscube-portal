import os
import shutil
import subprocess
import glob

folders = ['20260722', '20260723']
for folder in folders:
    for f in glob.glob(f'daily_import/{folder}/*.html'):
        filename = os.path.basename(f)
        if filename == '1.html':
            dest_folder = 'sunitoman_myjuggler_scraper'
        elif filename == '2.html':
            dest_folder = 'sunitoman_newking_scraper'
        elif filename == '3.html':
            dest_folder = 'sunitoman_scraper'
        else:
            continue
            
        dest_path = os.path.join(dest_folder, filename)
        
        shutil.copy2(f, dest_path)
        print(f"Copied {f} to {dest_path}")
        subprocess.run(["python", "extract_machines.py"], cwd=dest_folder, check=True)
        os.remove(dest_path)
        print(f"Processed and deleted {dest_path}")
