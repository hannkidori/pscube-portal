from bs4 import BeautifulSoup

for f in ['1.html', '2.html', '3.html']:
    try:
        soup = BeautifulSoup(open(f'daily_import/{f}', encoding='utf-8', errors='ignore'), 'html.parser')
        rows = soup.find_all('tr')
        daibans = []
        for row in rows:
            for a in row.find_all('a'):
                if 'href' in a.attrs and 'detail' in a['href']:
                    text = a.get_text(strip=True)
                    if text.isdigit():
                        daibans.append(text)
        print(f'{f}: First machine = {daibans[0] if daibans else None}')
    except Exception as e:
        print(f'Error reading {f}: {e}')
