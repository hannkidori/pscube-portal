import glob, datetime, os, re
from bs4 import BeautifulSoup

files = glob.glob('daily_import/**/*.html', recursive=True)
files = [f for f in files if '_files' not in f]

for f in files:
    try:
        mtime = os.path.getmtime(f)
        dt = datetime.datetime.fromtimestamp(mtime)
        if dt.hour < 5:
            base_date = (dt - datetime.timedelta(days=1)).date()
        else:
            base_date = dt.date()
        
        date_offset = 0
        soup = BeautifulSoup(open(f, encoding='utf-8', errors='ignore'), 'html.parser')
        
        # Sunitoman logic
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
        else:
            # Megaface logic
            active_tabs = soup.find_all(class_=lambda c: c and ('active' in c or 'selected' in c or 'current' in c))
            for tab in active_tabs:
                text = tab.get_text(strip=True).replace('{', '本日').replace('O', '日前')
                if '日前' in text or '本日' in text:
                    if text == "本日":
                        date_offset = 0
                    else:
                        try:
                            date_offset = int(re.sub(r'[^0-9]', '', text)) if re.sub(r'[^0-9]', '', text) else 1
                        except:
                            pass
                    break
        
        target_date = (base_date - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")
        print(f"File: {f} -> Base: {base_date}, Offset: {date_offset}, Target: {target_date}")
    except Exception as e:
        print(f"Error on {f}: {e}")
