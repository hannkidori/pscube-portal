import os, glob, re

base_dir = r"C:\Users\taira\Desktop\pscube_scraper"

thead_new = """<thead>
                        <tr>
                            <th onclick="sortTable('台番')">台番 ⇅</th>
                            <th onclick="sortTable('累計ゲーム数')">G数 ⇅</th>
                            <th onclick="sortTable('BIG回数')">BIG ⇅</th>
                            <th onclick="sortTable('REG回数')">REG ⇅</th>
                            <th onclick="sortTable('推測差枚')">推測差枚 ⇅</th>
                            <th onclick="sortTable('REG確率')">REG確率 ⇅</th>
                            <th onclick="sortTable('最有力設定')">最有力設定 ⇅</th>
                            <th>ベイズ推定(設定割合%)</th>
                        </tr>
                    </thead>"""

sort_table_new = """function sortTable(key) {{
            if (!key) return;
            if (currentSortColumn === key) {{
                sortAsc = !sortAsc;
            }} else {{
                // 台番は昇順、それ以外（差枚、BIG等）は降順スタートが自然
                sortAsc = (key === '台番') ? true : false;
            }}
            currentSortColumn = key;

            currentData.sort((a, b) => {{
                let valA = a[key];
                let valB = b[key];
                
                if (key === '最有力設定') {{
                    if (valA < valB) return sortAsc ? -1 : 1;
                    if (valA > valB) return sortAsc ? 1 : -1;
                    return 0;
                }}
                
                // 台番、G数、BIG、REG、差枚、確率などはすべて数値比較
                valA = parseFloat(String(valA).replace(/[^0-9.-]+/g, "")) || 0;
                valB = parseFloat(String(valB).replace(/[^0-9.-]+/g, "")) || 0;
                
                if (valA < valB) return sortAsc ? -1 : 1;
                if (valA > valB) return sortAsc ? 1 : -1;
                return 0;
            }});
            renderTable(currentData);
        }}"""

script_end_new = """        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }}

        // 初期化処理（これを呼ばないとデータテーブルが空になる）
        if(uniqueDays.length > 0) {{
            selectDate(uniqueDays[0], dateButtonsContainer.firstChild);
        }}
    </script>"""

select_date_tail_new = """            currentSortColumn = '台番';
            sortAsc = true;
            currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番']));
            renderTable(currentData);
        }}"""


for py_file in glob.glob(os.path.join(base_dir, '**/generate_html.py'), recursive=True):
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace thead
    content = re.sub(r'<thead>.*?</thead>', thead_new, content, flags=re.DOTALL)

    # 2. Replace sortTable
    content = re.sub(r'function sortTable\(.*?renderTable\(currentData\);\s*\}', sort_table_new, content, flags=re.DOTALL)

    # 3. Replace script end (remove any existing selectDate initializations to avoid duplicates, then insert clean)
    # First, let's just find the switchTab function until </script>
    content = re.sub(r'function switchTab\(tabId\).*?</script>', script_end_new, content, flags=re.DOTALL)
    
    # Also clean up any rogue renderPredictions(); if they exist before switchTab
    content = re.sub(r'// 初期化処理.*?renderPredictions\(\);.*?if\(uniqueDays\.length > 0\).*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'renderPredictions\(\);\s*if\(uniqueDays\.length > 0\).*?\}', '', content, flags=re.DOTALL)

    # 4. Fix selectDate sorting state
    # We look for currentData.sort((a, b) => parseInt(a['台番']) - parseInt(b['台番'])); renderTable(currentData); }
    # and prepend the state resets if they aren't there
    if "currentSortColumn = '台番';" not in content:
        content = re.sub(r'currentData\.sort\(\(a, b\) => parseInt\(a\[\'台番\'\]\) - parseInt\(b\[\'台番\'\]\)\);\s*renderTable\(currentData\);\s*\}', select_date_tail_new, content)
        
    with open(py_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed {py_file}')

    # Auto-run the updated script to generate the HTML
    os.system(f'python "{py_file}"')
