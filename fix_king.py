with open(r'C:\Users\taira\Desktop\pscube_scraper\megaface_king_scraper\generate_html.py', 'r', encoding='utf-8') as f:
    content = f.read()

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

if 'dropdown_html = f"""\n<div' not in content:
    content = content.replace('html_content = f"""<!DOCTYPE html>', dropdown_logic + '\nhtml_content = f"""<!DOCTYPE html>')
    
with open(r'C:\Users\taira\Desktop\pscube_scraper\megaface_king_scraper\generate_html.py', 'w', encoding='utf-8') as f:
    f.write(content)
