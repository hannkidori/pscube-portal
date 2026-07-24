import glob
import datetime
import os

for py_file in glob.glob('sunitoman*scraper/extract_machines.py'):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace the `base_date = dt.date()` logic with `hour < 5` logic.
    old_logic = "    base_date = dt.date()"
    new_logic = """    if dt.hour < 5:
        base_date = (dt - datetime.timedelta(days=1)).date()
    else:
        base_date = dt.date()"""
        
    if old_logic in content and 'hour < 5' not in content:
        content = content.replace(old_logic, new_logic)
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {py_file}")
    elif 'hour < 5' in content:
        print(f"Already fixed {py_file}")
    else:
        print(f"Could not find old_logic in {py_file}")
