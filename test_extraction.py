import glob, datetime, os
from bs4 import BeautifulSoup

for folder in ['20260722', '20260723']:
    for f in glob.glob(f'daily_import/{folder}/*.html'):
        if '3' in f or '1' in f or '2' in f or 'ドラゴン' in f:
            try:
                mtime = os.path.getmtime(f)
                dt = datetime.datetime.fromtimestamp(mtime)
                base_date = dt.date()
                
                date_offset = 0
                soup = BeautifulSoup(open(f, encoding='utf-8', errors='ignore'), 'html.parser')
                active_tabs = soup.find_all(class_='is-active')
                if active_tabs:
                    date_text = active_tabs[-1].get_text(strip=True)
                    if r'\u' in date_text:
                        date_text = date_text.encode('utf-8', errors='ignore').decode('unicode_escape', errors='ignore')
                        
                    if '昨日' in date_text:
                        date_offset = 1
                    elif '日前' in date_text:
                        try:
                            date_offset = int(date_text.replace('日前', ''))
                        except:
                            pass
                
                target_date = (base_date - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")
                print(f"File: {f} -> Base: {base_date}, Offset: {date_offset}, Target: {target_date}")
            except Exception as e:
                print(f"Error on {f}: {e}")
