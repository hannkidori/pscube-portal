import re, glob
files = glob.glob('daily_import_archive/*.html')
for f in files:
    content = open(f, encoding='utf-8', errors='ignore').read()
    match = re.search(r'<p class="day.*?>(.*?)</p>', content)
    if match:
        date = match.group(1).strip()
        if '07-14' in date or '07-16' in date or '07/14' in date or '07/16' in date:
            print(f"{f}: {date}")
