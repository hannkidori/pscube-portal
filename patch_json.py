import glob
import os

for file in glob.glob('*/generate_html.py'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'with open("ranking.json"' not in content:
        target = 'json_predictions = json.dumps(predictions, ensure_ascii=False)'
        replacement = 'json_predictions = json.dumps(predictions, ensure_ascii=False)\nwith open("ranking.json", "w", encoding="utf-8") as f:\n    f.write(json_predictions)'
        if target in content:
            content = content.replace(target, replacement)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print('Updated', file)
        else:
            print('Target not found in', file)
