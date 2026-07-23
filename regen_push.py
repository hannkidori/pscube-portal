import glob
import subprocess
import os

scrapers = glob.glob('*_scraper')
for scraper in scrapers:
    script_path = os.path.join(scraper, 'generate_html.py')
    if os.path.exists(script_path):
        print(f"Running {script_path}...")
        subprocess.run(['python', 'generate_html.py'], cwd=scraper, check=True)

subprocess.run(['git', 'add', '.'], check=True)
subprocess.run(['git', 'commit', '-m', 'Fix swapped 21st data for Sunitoman'], check=True)
subprocess.run(['git', 'push'], check=True)
print("Pushed to GitHub!")
