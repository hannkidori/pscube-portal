import os
import re

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
            
        # Patch the card title
        old_card = '<span>${{rank}} / 台番 ${{p.台番}}</span>'
        new_card = '<span>${{rank}} / 台番 <span style="${{getCornerStyle(p.台番)}}">${{p.台番}}</span></span>'
        if old_card in content:
            content = content.replace(old_card, new_card)
            
        # Patch the table row
        old_td = '<td><strong>${{row[\'台番\']}}</strong></td>'
        new_td = '<td><strong style="${{getCornerStyle(row[\'台番\'])}}">${{row[\'台番\']}}</strong></td>'
        if old_td in content:
            content = content.replace(old_td, new_td)
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Repatched {folder}/generate_html.py")
