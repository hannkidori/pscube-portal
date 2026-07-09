import os

base_dir = r'C:\Users\taira\Desktop\pscube_scraper'
megaface_folders = ['megaface_newking_scraper', 'megaface_king_scraper', 'megaface_myjuggler_scraper']

for folder in megaface_folders:
    py_file = os.path.join(base_dir, folder, 'extract_machines.py')
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_logic = '''        reference_date = dt
        if dt.hour < 9:
            reference_date = dt - datetime.timedelta(days=1)
            
        days_ago = 0
        active_tab = soup.find('li', class_='is-active')
        if active_tab:
            tab_text = active_tab.get_text(strip=True)
            if "日前" in tab_text:
                try:
                    days_ago = int(tab_text.replace("日前", ""))
                except:
                    pass
            elif "昨日" in tab_text:
                days_ago = 1
                
        if days_ago == 0:
            actual_date = reference_date
        else:
            actual_date = reference_date - datetime.timedelta(days=days_ago)'''
            
    new_logic = '''        days_ago = 0
        active_tab = soup.find('li', class_='is-active')
        if active_tab:
            tab_text = active_tab.get_text(strip=True)
            if "日前" in tab_text:
                try:
                    days_ago = int(tab_text.replace("日前", ""))
                except:
                    pass
            elif "昨日" in tab_text:
                days_ago = 1
                
        if dt.hour < 9 and days_ago == 0:
            actual_date = dt - datetime.timedelta(days=1)
        else:
            actual_date = dt - datetime.timedelta(days=days_ago)'''
            
    content = content.replace(old_logic, new_logic)
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Fixed {folder}")

sunitoman_folders = ['sunitoman_scraper', 'sunitoman_newking_scraper', 'sunitoman_myjuggler_scraper']

for folder in sunitoman_folders:
    py_file = os.path.join(base_dir, folder, 'extract_machines.py')
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_suni = '''    now = datetime.datetime.now()
    if now.hour < 9:
        now = now - datetime.timedelta(days=1)
    
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
    
    target_date = (now - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")'''
    
    new_suni = '''    mtime = os.path.getmtime(filepath)
    now = datetime.datetime.fromtimestamp(mtime)
    
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
                
    if now.hour < 9 and date_offset == 0:
        now = now - datetime.timedelta(days=1)
    
    target_date = (now - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")'''
    
    content = content.replace(old_suni, new_suni)
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Fixed {folder}")
