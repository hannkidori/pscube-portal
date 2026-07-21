import os
import subprocess
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
scrapers = [
    'megaface_king_scraper',
    'megaface_newking_scraper',
    'megaface_myjuggler_scraper',
    'sunitoman_scraper',
    'sunitoman_newking_scraper',
    'sunitoman_myjuggler_scraper'
]

# get all dates
dates = set()
for folder in scrapers:
    csv_path = os.path.join(base_dir, folder, 'master_data.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        for d in df['日付'].unique():
            dates.add(d)

dates = sorted(list(dates))
print(f"Dates to regenerate: {dates}")

for folder in scrapers:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path): continue
    for date_str in dates:
        subprocess.run(['python', 'generate_html.py', date_str], cwd=folder_path)

print("Updating portal...")
subprocess.run(['python', 'update_portal.py'], cwd=base_dir)

print("Pushing to git...")
subprocess.run(['git', 'add', '.'], cwd=base_dir)
subprocess.run(['git', 'commit', '-m', 'Fix syntax error and regenerate html with corner styles'], cwd=base_dir)
subprocess.run(['git', 'push', 'origin', 'main'], cwd=base_dir)
