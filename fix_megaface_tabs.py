import os

base_dir = r'C:\Users\taira\Desktop\pscube_scraper'
megaface_folders = ['megaface_newking_scraper', 'megaface_king_scraper', 'megaface_myjuggler_scraper']

for folder in megaface_folders:
    py_file = os.path.join(base_dir, folder, 'extract_machines.py')
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_logic = '''        days_ago = 0
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
            actual_date = dt - datetime.timedelta(days=days_ago)
            
        date_str = actual_date.strftime("%Y-%m-%d")'''
        
    new_logic = '''        days_ago = 0
        date_str = None
        active_tab = soup.find('li', class_=['selected', 'is-active'])
        if active_tab:
            if active_tab.has_attr('data-ymd'):
                ymd = active_tab['data-ymd']
                if len(ymd) == 8:
                    date_str = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
            
            if not date_str:
                tab_text = active_tab.get_text(strip=True)
                if "日前" in tab_text:
                    try:
                        days_ago = int(tab_text.replace("日前", ""))
                    except:
                        pass
                elif "昨日" in tab_text:
                    days_ago = 1
                    
        if not date_str:
            if dt.hour < 9 and days_ago == 0:
                actual_date = dt - datetime.timedelta(days=1)
            else:
                actual_date = dt - datetime.timedelta(days=days_ago)
            date_str = actual_date.strftime("%Y-%m-%d")'''
            
    content = content.replace(old_logic, new_logic)
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Fixed {folder}")
