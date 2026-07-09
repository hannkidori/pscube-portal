import os, glob, re

base_dir = r'C:\Users\taira\Desktop\pscube_scraper'

for py_file in glob.glob(os.path.join(base_dir, '**/generate_html.py'), recursive=True):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove the broken dropdown_builder if it's there
    content = re.sub(r'options_html = ""\nfor i, d in enumerate\(all_dates\):.*?</select>\n</div>\n"""\n', '', content, flags=re.DOTALL)
    
    # Let's insert the data filtering logic BEFORE machine_history
    filter_logic = """
import sys
original_data = data.copy()
if len(sys.argv) > 1:
    target_date_str = sys.argv[1]
    data = [r for r in data if r["日付"] <= target_date_str]
    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"report_{target_date_str}.html")
else:
    html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.html")

all_dates = sorted(list(set(r["日付"] for r in original_data)), reverse=True)
"""
    if 'original_data = data.copy()' not in content:
        content = content.replace('machine_history = defaultdict(list)', filter_logic + '\nmachine_history = defaultdict(list)')

    # Build the dropdown_html AFTER last_date_str is defined
    dropdown_logic = """
options_html = ""
for i, d in enumerate(all_dates):
    selected = "selected" if d == last_date_str else ""
    val = "report.html" if i == 0 else f"report_{d}.html"
    label = f"{d} (最新)" if i == 0 else d
    options_html += f'<option value="{val}" {selected}>{label}</option>\\n'

dropdown_html = f\"\"\"
<div style="text-align: center; margin-bottom: 1.5rem; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; display: inline-block;">
    <span style="color: #00d2d3; font-weight: bold; margin-right: 10px;">📅 表示中のデータ: </span>
    <select onchange="window.location.href=this.value" style="padding: 8px 15px; border-radius: 5px; background: #2f3542; color: #fff; border: 1px solid #00d2d3; cursor: pointer; font-size: 1rem; font-weight: bold; outline: none;">
        {options_html}
    </select>
</div>
\"\"\"
"""
    if 'dropdown_html = f' not in content:
        content = content.replace('html_content = f"""<!DOCTYPE html>', dropdown_logic + '\nhtml_content = f"""<!DOCTYPE html>')
        
    # Ensure `{dropdown_html}` is safely injected
    if '{dropdown_html}' not in content:
        content = content.replace('</header>', '</header>\n        <div style="text-align: center;">\n            {dropdown_html}\n        </div>')

    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f'Fixed {py_file}')
