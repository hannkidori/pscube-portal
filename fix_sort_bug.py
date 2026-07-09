import glob
import os
import subprocess
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

for py_file in glob.glob("*/generate_html.py"):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove the global injection
    bad_injection = "currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番']));\n            renderTable(currentData);"
    content = content.replace(bad_injection, "renderTable(currentData);")
    
    # 2. Inject it ONLY in loadData
    # Look for: document.getElementById('tableContainer').classList.add('active');\n            \n            renderTable(currentData);
    good_target = "document.getElementById('tableContainer').classList.add('active');\n            \n            renderTable(currentData);"
    if good_target in content:
        content = content.replace(
            good_target,
            "document.getElementById('tableContainer').classList.add('active');\n            \n            currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番']));\n            renderTable(currentData);"
        )

    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Fixed sorting bug in {py_file}")

# Regenerate HTMLs
for folder in [f.replace('\\\\', '/').split('/')[0] for f in glob.glob("*/generate_html.py")]:
    try:
        subprocess.run(["python", "generate_html.py"], cwd=os.path.join(base_dir, folder))
    except Exception as e:
        pass
