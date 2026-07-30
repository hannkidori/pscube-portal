import glob, os
from bs4 import BeautifulSoup

for f in glob.glob('daily_import/**/*.html', recursive=True):
    if '_files' in f or not os.path.basename(f) in ['1.html', '2.html', '3.html']:
        continue
    try:
        soup = BeautifulSoup(open(f, encoding='utf-8', errors='ignore'), 'html.parser')
        daibans = [a.get_text(strip=True) for a in soup.find_all('a') if 'href' in a.attrs and 'detail' in a['href'] and a.get_text(strip=True).isdigit()]
        print(f'{f}: First machine = {daibans[0] if daibans else None}')
    except Exception as e:
        print(f'Error reading {f}: {e}')
