import glob
import re
import os
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))

for py_file in glob.glob("*/generate_html.py"):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Move active class from prediction button to data button
    content = content.replace('class="tab-btn active" onclick="switchTab(\'prediction\')"', 'class="tab-btn" onclick="switchTab(\'prediction\')"')
    content = content.replace('class="tab-btn" onclick="switchTab(\'data\')"', 'class="tab-btn active" onclick="switchTab(\'data\')"')
    
    # Move active class from prediction content to data content
    content = content.replace('id="prediction" class="tab-content active"', 'id="prediction" class="tab-content"')
    content = content.replace('id="data" class="tab-content"', 'id="data" class="tab-content active"')

    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Updated default tab in {py_file}")

# Regenerate HTMLs
for folder in [f.replace('\\\\', '/').split('/')[0] for f in glob.glob("*/generate_html.py")]:
    try:
        subprocess.run(["python", "generate_html.py"], cwd=os.path.join(base_dir, folder))
    except Exception as e:
        print(f"Error running generate_html.py in {folder}: {e}")
