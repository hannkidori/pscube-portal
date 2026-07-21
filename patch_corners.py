import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

scrapers = [
    ('megaface_king_scraper', 'MEGAFACE', 'キング'),
    ('megaface_myjuggler_scraper', 'MEGAFACE', 'マイジャグラー'),
    ('megaface_newking_scraper', 'MEGAFACE', 'ニューキング'),
    ('sunitoman_scraper', 'SUNITOMAN', 'ドラゴン'),
    ('sunitoman_newking_scraper', 'SUNITOMAN', 'ニューキング'),
    ('sunitoman_myjuggler_scraper', 'SUNITOMAN', 'マイジャグラー')
]

js_function = """
        function getCornerStyle(daiban) {
            daiban = parseInt(daiban);
            let corner = null;
            const store = '%s';
            const machine = '%s';
            
            if (store === 'MEGAFACE') {
                if (machine === 'マイジャグラー') {
                    if (daiban === 543 || daiban === 544) corner = 'aisle';
                    if (daiban === 533 || daiban === 554) corner = 'opposite';
                } else if (machine === 'キング') {
                    if (daiban === 390) corner = 'aisle';
                    if (daiban === 373) corner = 'opposite';
                } else if (machine === 'ニューキング') {
                    if ([319, 354, 355].includes(daiban)) corner = 'aisle';
                    if ([336, 337, 372].includes(daiban)) corner = 'opposite';
                }
            } else if (store === 'SUNITOMAN') {
                if (machine === 'ドラゴン') {
                    if (daiban === 396 || daiban === 425) corner = 'aisle';
                    if (daiban === 410 || daiban === 411) corner = 'opposite';
                } else if (machine === 'ニューキング') {
                    if (daiban === 336 || daiban === 365) corner = 'aisle';
                    if (daiban === 350 || daiban === 351) corner = 'opposite';
                } else if (machine === 'マイジャグラー') {
                    if (daiban === 273 || daiban === 304) corner = 'aisle';
                    if (daiban === 278 || daiban === 299) corner = 'opposite';
                }
            }
            
            if (corner === 'aisle') return 'background: rgba(255, 60, 60, 0.4); padding: 2px 6px; border-radius: 4px; font-weight: bold; color: white;';
            if (corner === 'opposite') return 'background: rgba(60, 100, 255, 0.4); padding: 2px 6px; border-radius: 4px; font-weight: bold; color: white;';
            return '';
        }
"""

for folder, store, machine in scrapers:
    path = os.path.join(base_dir, folder, 'generate_html.py')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Inject the JS function if not already there
        if 'function getCornerStyle' not in content:
            injected_js = js_function % (store, machine)
            content = content.replace('const dateButtonsContainer = document.getElementById', injected_js + '\n        const dateButtonsContainer = document.getElementById')
            
        # 2. Patch the card title
        old_card = '<span>${rank} / 台番 ${p.台番}</span>'
        new_card = '<span>${rank} / 台番 <span style="${getCornerStyle(p.台番)}">${p.台番}</span></span>'
        if old_card in content:
            content = content.replace(old_card, new_card)
            
        # 3. Patch the table row
        old_td = '<td><strong>${row[\'台番\']}</strong></td>'
        new_td = '<td><strong style="${getCornerStyle(row[\'台番\'])}">${row[\'台番\']}</strong></td>'
        if old_td in content:
            content = content.replace(old_td, new_td)
            
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {folder}/generate_html.py")
