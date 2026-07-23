import glob
import re

for py_file in glob.glob('sunitoman*scraper/extract_machines.py'):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # We want to replace the logic that uses datetime.datetime.now() or datetime.fromtimestamp(mtime) with the hour<9 shift
    # and replace it with simple mtime -> base_date
    
    # Logic in sunitoman_scraper:
    content = re.sub(
        r'now = datetime\.datetime\.now\(\).*?target_date = \(now - datetime\.timedelta\(days=date_offset\)\)\.strftime\("%Y-%m-%d"\)',
        '''mtime = os.path.getmtime(html_file)
    dt = datetime.datetime.fromtimestamp(mtime)
    base_date = dt.date()
    
    date_offset = 0
    active_tabs = soup.find_all(class_='is-active')
    if active_tabs:
        date_text = active_tabs[-1].get_text(strip=True)
        if r'\\u' in date_text:
            date_text = date_text.encode('utf-8', errors='ignore').decode('unicode_escape', errors='ignore')
            
        if '昨日' in date_text:
            date_offset = 1
        elif '日前' in date_text:
            try:
                date_offset = int(date_text.replace('日前', ''))
            except:
                pass
    
    target_date = (base_date - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")''',
        content, flags=re.DOTALL
    )

    # Logic in the other scrapers:
    content = re.sub(
        r'now = datetime\.datetime\.fromtimestamp\(mtime\).*?target_date = \(now - datetime\.timedelta\(days=date_offset\)\)\.strftime\("%Y-%m-%d"\)',
        '''dt = datetime.datetime.fromtimestamp(mtime)
    base_date = dt.date()
    
    date_offset = 0
    active_tabs = soup.find_all(class_='is-active')
    if active_tabs:
        date_text = active_tabs[-1].get_text(strip=True)
        if r'\\u' in date_text:
            date_text = date_text.encode('utf-8', errors='ignore').decode('unicode_escape', errors='ignore')
            
        if '昨日' in date_text:
            date_offset = 1
        elif '日前' in date_text:
            try:
                date_offset = int(date_text.replace('日前', ''))
            except:
                pass
                
    target_date = (base_date - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")''',
        content, flags=re.DOTALL
    )
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {py_file}")
