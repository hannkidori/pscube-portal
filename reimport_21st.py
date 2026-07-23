import os
import subprocess

archive_dir = "daily_import_archive"
files_to_import = [
    (os.path.join(archive_dir, "1.html"), "sunitoman_myjuggler_scraper"),
    (os.path.join(archive_dir, "2.html"), "sunitoman_newking_scraper"),
    (os.path.join(archive_dir, "3.html"), "sunitoman_scraper")
]

for html_file, scraper_dir in files_to_import:
    if os.path.exists(html_file):
        print(f"Re-importing {html_file} into {scraper_dir}")
        import_script = os.path.join(scraper_dir, "extract_machines.py")
        subprocess.run(["python", import_script, f"../{html_file}"], cwd=scraper_dir, check=True)
