import glob
import os

for f in glob.glob('sunitoman*scraper/extract_machines.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('now = datetime.datetime.fromtimestamp(mtime)', 'dt = datetime.datetime.fromtimestamp(mtime)\\n    base_date = dt.date()')
    content = content.replace('now = datetime.datetime.now()', 'mtime = os.path.getmtime(html_file)\\n    dt = datetime.datetime.fromtimestamp(mtime)\\n    base_date = dt.date()')
    content = content.replace('if now.hour < 9:\\n        now = now - datetime.timedelta(days=1)\\n    ', '')
    content = content.replace('if now.hour < 9 and date_offset == 0:\\n        now = now - datetime.timedelta(days=1)\\n    ', '')
    content = content.replace('target_date = (now - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")', 'target_date = (base_date - datetime.timedelta(days=date_offset)).strftime("%Y-%m-%d")')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f'Fixed {f}')
