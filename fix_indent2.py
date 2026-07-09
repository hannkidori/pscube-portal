import glob

for f in glob.glob('*/generate_html.py'):
    with open(f, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Let's completely rewrite the opening block
    out_lines = []
    in_open_block = False
    
    for i, line in enumerate(lines):
        if "# Auto‑detect CSV encoding using chardet" in line or "# Auto-detect CSV encoding using chardet" in line:
            # Check if previous line is "if os.path.exists(csv_file):"
            has_if = (i > 0 and "if os.path.exists(" in lines[i-1])
            indent = "    " if has_if else ""
            
            # Write the block manually
            out_lines.append(f"{indent}import chardet\n") # Just in case
            out_lines.append(f"{indent}with open(csv_file, 'rb') as f_raw:\n")
            out_lines.append(f"{indent}    raw_bytes = f_raw.read()\n")
            out_lines.append(f"{indent}    detected = chardet.detect(raw_bytes)\n")
            out_lines.append(f"{indent}    enc = detected['encoding'] or 'utf-8'\n")
            out_lines.append(f"{indent}with open(csv_file, 'r', encoding=enc) as f:\n")
            
            in_open_block = True
            
        elif in_open_block:
            if "reader = csv.DictReader" in line:
                in_open_block = False
                out_lines.append(line) # preserve indent of reader
            elif "enc = detected" in line or "raw_bytes =" in line or "detected =" in line or "with open(" in line:
                pass # skip old broken lines
            else:
                pass # skip
        else:
            out_lines.append(line)
            
    with open(f, 'w', encoding='utf-8') as file:
        file.writelines(out_lines)
