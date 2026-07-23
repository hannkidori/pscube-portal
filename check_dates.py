import glob
from bs4 import BeautifulSoup
import re

for folder in ['20260722', '20260723']:
    files = glob.glob(f'daily_import/{folder}/*.html')
    for f in files:
        if '3' in f or '1' in f or '2' in f:
            content = open(f, encoding='utf-8', errors='ignore').read()
            soup = BeautifulSoup(content, 'html.parser')
            active = soup.find_all(class_='is-active')
            if active:
                date_text = active[-1].get_text(strip=True)
                if r'\u' in date_text:
                    date_text = date_text.encode('utf-8', errors='ignore').decode('unicode_escape', errors='ignore')
                print(f"{f}: {date_text}")
            else:
                match = re.search(r'<p class="day.*?>(.*?)</p>', content)
                print(f"{f}: {match.group(1) if match else 'No date'}")
