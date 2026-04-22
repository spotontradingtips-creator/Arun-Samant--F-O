
import os

manifest_path = r'c:\Antigravity\Arun Samant - F&O\IMMUTABLE_RULES.md'

with open(manifest_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if '| Trade P&L Reached | Locked Floor |' in line:
        new_lines.append("## 3. Trailing Stop Loss (TSL) Ladder\n")
        new_lines.append("| Stage | Side | Trade P&L Reached | Locked Floor | Gap (Cushion) |\n")
        new_lines.append("| :--- | :--- | :--- | :--- | :--- |\n")
        new_lines.append("| **Stage 1** | **SAFE** | ₹250 | **₹100** | ₹150 |\n")
        new_lines.append("| **Stage 2** | **BREATH** | ₹350 | **₹150** | ₹200 |\n")
        new_lines.append("| **Stage 3** | **CORE** | ₹700 | **₹500** | ₹200 |\n")
        new_lines.append("| **Stage 4** | **ADV** | ₹1,050 | **₹750** | ₹300 |\n")
        new_lines.append("| **Stage 5** | **LOCK** | ₹1,400 | **₹1,000** | ₹400 |\n")
        new_lines.append("| **Stage 6** | **MAX** | ₹1,750 | **₹1,250** | ₹500 |\n")
        skip = True
        continue
    
    if skip:
        if '|' in line or ':---' in line or '₹' in line:
            continue
        else:
            skip = False
    
    new_lines.append(line)

with open(manifest_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Manifest TSL updated successfully via Python.")
