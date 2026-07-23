import datetime, glob
from bs4 import BeautifulSoup

now = datetime.datetime.now()
if now.hour < 9:
    now = now - datetime.timedelta(days=1)

print(f"Base now is {now}")

for f in glob.glob('daily_import/20260723/*.html'):
    if '3' in f or '1' in f or '2' in f:
        soup = BeautifulSoup(open(f, encoding='utf-8', errors='ignore'), 'html.parser')
        active = soup.find_all(class_='is-active')
        if active:
            date_text = active[-1].get_text(strip=True)
            if r'\u' in date_text:
                date_text = date_text.encode('utf-8').decode('unicode_escape')
            date_offset = 0
            if '昨日' in date_text:
                date_offset = 1
            elif '日前' in date_text:
                try:
                    date_offset = int(date_text.replace('日前', ''))
                except:
                    pass
            target_date = (now - datetime.timedelta(days=date_offset)).strftime('%Y-%m-%d')
            print(f"{f} parsed as {target_date} (offset={date_offset}, text={date_text.encode('utf-8')})")
