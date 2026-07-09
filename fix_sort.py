import glob
import re

for file in glob.glob("*/generate_html.py"):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Default sort by daiban
    target1 = "document.getElementById('tableContainer').classList.add('active');\n            \n            renderTable(currentData);"
    replace1 = "document.getElementById('tableContainer').classList.add('active');\n            \n            currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番']));\n            renderTable(currentData);"
    
    # Alternatively, target the renderTable(currentData) directly
    if "currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番']));" not in content:
        content = content.replace(
            "renderTable(currentData);",
            "currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番']));\n            renderTable(currentData);"
        )

    # Fix 2: parseFloat replace bug
    content = content.replace(
        "valA = parseFloat(valA.replace(/[^0-9.-]+/g, \"\") || \"0\");",
        "valA = parseFloat(String(valA).replace(/[^0-9.-]+/g, \"\")) || 0;"
    )
    content = content.replace(
        "valB = parseFloat(valB.replace(/[^0-9.-]+/g, \"\") || \"0\");",
        "valB = parseFloat(String(valB).replace(/[^0-9.-]+/g, \"\")) || 0;"
    )

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {file}")

import subprocess
for folder in [f.replace('\\\\', '/').split('/')[0] for f in glob.glob("*/generate_html.py")]:
    try:
        subprocess.run(["python", "generate_html.py"], cwd=folder)
    except:
        pass
