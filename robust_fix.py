import glob
import re

for py_file in glob.glob('sunitoman*scraper/extract_machines.py'):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to find the variable name for the file being processed.
    # In process_file(html_file): it's html_file.
    # In process_file(filepath): it's filepath.
    file_var = "html_file" if "process_file(html_file)" in content else "filepath"

    # Replace the existing date logic (from 'now =' to 'target_date =')
    # Note: sunitoman_myjuggler_scraper already had some mtime logic, but we'll overwrite it uniformly.
    
    pattern = r'(?:now = datetime\.datetime\.(?:now|fromtimestamp)\(.*?\).*?target_date = \(now - datetime\.timedelta\(days=date_offset\)\)\.strftime\("%Y-%m-%d"\))'
    
    # We also need to remove the `now = datetime...` if it exists, but since regex across multiple lines can be tricky,
    # let's just use string slicing based on '# 日付の決定' (or similar markers) up to 'target_date ='
    
    if '# 日付の決定' in content:
        start_idx = content.find('# 日付の決定')
    elif 'mtime = os.path.getmtime(filepath)' in content:
        start_idx = content.find('mtime = os.path.getmtime(filepath)')
    else:
        start_idx = content.find('now = datetime.datetime.now()')
        
    end_idx = content.find('target_date =', start_idx)
    end_idx = content.find('\\n', end_idx) # go to end of line
    
    old_logic = content[start_idx:end_idx]
    
    new_logic = f"""mtime = os.path.getmtime({file_var})
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
                
    target_date = (base_date - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")"""
    
    content = content.replace(old_logic, new_logic)
    
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Fixed {py_file} using variable {file_var}")
