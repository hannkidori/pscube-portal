import glob
for f in glob.glob('*/generate_html.py'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix indentations
    content = content.replace('\nwith open(csv_file, "rb") as f_raw:', '\n    with open(csv_file, "rb") as f_raw:')
    content = content.replace('\n    raw_bytes = f_raw.read()', '\n        raw_bytes = f_raw.read()')
    content = content.replace('\n    detected = chardet.detect(raw_bytes)', '\n        detected = chardet.detect(raw_bytes)')
    content = content.replace('\n    enc = detected[\'encoding\'] or \'utf-8\'', '\n        enc = detected[\'encoding\'] or \'utf-8\'')
    content = content.replace('\nwith open(csv_file, "r", encoding=enc) as f:', '\n    with open(csv_file, "r", encoding=enc) as f:')

    # Fix SyntaxError: f-string: single '}' is not allowed
    # Sometimes }}} might have been created by my previous regex.
    content = content.replace('}}}', '}}')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
