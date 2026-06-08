import re

with open("frontend-backup/roadmap.html", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")
grid_start = -1
for i, line in enumerate(lines):
    if "class=\"layout-grid\"" in line:
        grid_start = i
        break

if grid_start != -1:
    print(f"layout-grid starts at line {grid_start+1}")
    div_level = 0
    in_grid = False
    children_starts = []
    for idx in range(grid_start, len(lines)):
        line = lines[idx]
        div_opens = len(re.findall(r'<div', line))
        div_closes = len(re.findall(r'</div', line))
        
        if "class=\"layout-grid\"" in line:
            div_level = 1
            in_grid = True
            continue
            
        if in_grid:
            old_level = div_level
            div_level += (div_opens - div_closes)
            
            if old_level == 1 and div_opens > 0:
                children_starts.append(idx)
                
            if div_level == 0:
                break
                
    print("Children starts:")
    for child_idx in children_starts:
        print(f"Child at line {child_idx+1}: {lines[child_idx].strip().encode('ascii', 'ignore').decode('ascii')}")
        for offset in range(15):
            if child_idx + offset < len(lines):
                print(f"  {lines[child_idx+offset].strip().encode('ascii', 'ignore').decode('ascii')}")
else:
    print("layout-grid not found.")
