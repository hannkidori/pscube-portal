import os
import shutil
import subprocess

tasks = [
    ("daily_import_archive/1.html", "sunitoman_myjuggler_scraper", "1.html"),
    ("daily_import_archive/2.html", "sunitoman_newking_scraper", "2.html"),
    ("daily_import_archive/3.html", "sunitoman_scraper", "3.html")
]

for src, folder, dest_name in tasks:
    if os.path.exists(src):
        dest_path = os.path.join(folder, dest_name)
        shutil.copy2(src, dest_path)
        print(f"Copied {src} to {dest_path}")
        subprocess.run(["python", "extract_machines.py"], cwd=folder, check=True)
        os.remove(dest_path)
        print(f"Processed and deleted {dest_path}")
