import sys, glob
sys.path.append('sunitoman_scraper')
from extract_machines import process_file

files = glob.glob('daily_import_archive/*.html')
for f in files:
    content = open(f, encoding='utf-8', errors='ignore').read()
    if 'ドラゴン' in content:
        print('Target:', f)
        res = process_file(f)
        print("Found:", len(res))
        for r in res[:2]:
            print(r['日付'], r['機種名'], r['台番'])
