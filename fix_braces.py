import os

base_dir = os.path.dirname(os.path.abspath(__file__))

scrapers = [
    'megaface_king_scraper',
    'megaface_myjuggler_scraper',
    'megaface_newking_scraper',
    'sunitoman_scraper',
    'sunitoman_newking_scraper',
    'sunitoman_myjuggler_scraper'
]

for folder in scrapers:
    path = os.path.join(base_dir, folder, 'generate_html.py')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # The injected function was:
        # function getCornerStyle(daiban) { ... }
        # Let's fix the braces
        import re
        
        def fix_braces(match):
            text = match.group(0)
            # escape braces
            text = text.replace('{', '{{').replace('}', '}}')
            return text
            
        content = re.sub(r'function getCornerStyle\(daiban\) \{.*?\n        \}', fix_braces, content, flags=re.DOTALL)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed braces in {folder}")
