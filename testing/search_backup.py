with open("frontend-backup/roadmap.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
    
# Find grid or column classes
for i, line in enumerate(lines):
    if "class=" in line and ("grid" in line or "column" in line or "side" in line or "coach" in line):
        clean_line = line.strip().encode('ascii', 'ignore').decode('ascii')
        print(f"Line {i+1}: {clean_line}")
