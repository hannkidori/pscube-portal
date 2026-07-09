import glob
import os
import subprocess

base_dir = os.path.dirname(os.path.abspath(__file__))

button_html = """    <div class="container">
        <div style="margin-bottom: 1rem;">
            <a href="../index.html" style="display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.1); color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 12px; font-weight: bold; transition: background 0.3s; border: 1px solid rgba(255,255,255,0.2);" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">
                <span style="font-size: 1.2rem;">🏠</span> ポータルへ戻る
            </a>
        </div>"""

for py_file in glob.glob("*/generate_html.py"):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if "ポータルへ戻る" not in content:
        content = content.replace('    <div class="container">', button_html)

        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Added Home button to {py_file}")

# Regenerate HTMLs
for folder in [f.replace('\\\\', '/').split('/')[0] for f in glob.glob("*/generate_html.py")]:
    try:
        subprocess.run(["python", "generate_html.py"], cwd=os.path.join(base_dir, folder))
    except Exception as e:
        print(f"Error running generate_html.py in {folder}: {e}")
