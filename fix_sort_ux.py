import glob
import os
import subprocess
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

old_code = """            if (currentSortColumn === columnIndex) {
                sortAsc = !sortAsc;
            } else {
                sortAsc = true;
                currentSortColumn = columnIndex;
            }"""

new_code = """            if (currentSortColumn === columnIndex) {
                sortAsc = !sortAsc;
            } else {
                if (key === '台番' || key === 'REG確率') {
                    sortAsc = true;
                } else {
                    sortAsc = false;
                }
                currentSortColumn = columnIndex;
            }"""

for py_file in glob.glob("*/generate_html.py"):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # The code uses double braces {{ and }} because it's inside an f-string!
    old_code_fstring = old_code.replace("{", "{{").replace("}", "}}")
    new_code_fstring = new_code.replace("{", "{{").replace("}", "}}")
    
    if old_code_fstring in content:
        content = content.replace(old_code_fstring, new_code_fstring)
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched UX sort bug in {py_file}")
    else:
        print(f"Could not find target code in {py_file}")

# Regenerate HTMLs
for folder in [f.replace('\\\\', '/').split('/')[0] for f in glob.glob("*/generate_html.py")]:
    try:
        subprocess.run(["python", "generate_html.py"], cwd=os.path.join(base_dir, folder))
    except Exception as e:
        pass
