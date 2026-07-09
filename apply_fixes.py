import os, glob, re

base_dir = r'C:\Users\taira\Desktop\pscube_scraper'

for py_file in glob.glob(os.path.join(base_dir, '**/generate_html.py'), recursive=True):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Add sys import and logic right after reading csv
    if 'import sys' not in content:
        content = content.replace('import csv', 'import csv\nimport sys')
        
    read_csv_logic = '''    for row in reader:
        data.append(row)'''
        
    new_logic = '''    for row in reader:
        data.append(row)

original_data = data.copy()
if len(sys.argv) > 1:
    target_date_str = sys.argv[1]
    data = [r for r in data if r["日付"] <= target_date_str]
    html_file = f"report_{target_date_str}.html"
else:
    html_file = "report.html"
    
all_dates = sorted(list(set(r["日付"] for r in original_data)), reverse=True)
'''
    if 'original_data = data.copy()' not in content:
        content = content.replace(read_csv_logic, new_logic)
        
    # 2. Build dropdown HTML right before html_content definition
    dropdown_builder = '''
options_html = ""
for i, d in enumerate(all_dates):
    selected = "selected" if d == last_date_str else ""
    # Latest date always points to report.html to act as default
    val = "report.html" if i == 0 else f"report_{d}.html"
    label = f"{d} (最新)" if i == 0 else d
    options_html += f'<option value="{val}" {selected}>{label}</option>\\n'

dropdown_html = f"""
<div style="text-align: center; margin-bottom: 1.5rem; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; display: inline-block;">
    <span style="color: #00d2d3; font-weight: bold; margin-right: 10px;">📅 表示中のデータ: </span>
    <select onchange="window.location.href=this.value" style="padding: 8px 15px; border-radius: 5px; background: #2f3542; color: #fff; border: 1px solid #00d2d3; cursor: pointer; font-size: 1rem; font-weight: bold; outline: none;">
        {options_html}
    </select>
</div>
"""

html_content = f"""<!DOCTYPE html>'''

    if 'dropdown_html = f' not in content:
        content = content.replace('html_content = f"""<!DOCTYPE html>', dropdown_builder)

    # 3. Add noindex to head
    if 'noindex, nofollow' not in content:
        content = content.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta name="robots" content="noindex, nofollow">')
        
    # 4. Inject dropdown_html after </header>
    if '{dropdown_html}' not in content:
        content = content.replace('</header>', '</header>\n        <div style="text-align: center;">\n            {dropdown_html}\n        </div>')

    # 5. Fix writing to correct file name
    if 'with codecs.open(html_file,' not in content:
        content = content.replace('with codecs.open("report.html",', 'with codecs.open(html_file,')
        
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f'Updated {py_file}')
