import re

content = open('sunitoman_scraper/generate_html.py', encoding='utf-8').read()
matches = re.findall(r'<div class="machine-header">.*?</div>', content, re.DOTALL)
print(matches[0] if matches else "NOT FOUND")

matches2 = re.findall(r'<h2.*?>.*?</h2>', content, re.DOTALL)
for m in matches2: print(m)
