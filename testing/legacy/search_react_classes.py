import os
import re

src_dir = "frontend-react/src"
all_files = []
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file.endswith((".jsx", ".css")):
            all_files.append(os.path.join(root, file))

print(f"Searching {len(all_files)} files...")
for filepath in all_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find classes or IDs matching coach, ai, right, drawer, panel
    matches = re.findall(r'className="([^"]+)"|id="([^"]+)"|\.([a-zA-Z0-9_-]+)\s*\{', content)
    found = []
    for m in matches:
        # m is a tuple of (className, id, css_class)
        for val in m:
            if val and any(x in val.lower() for x in ["coach", "ai", "right", "drawer", "panel"]):
                found.append(val)
                
    if found:
        print(f"File {os.path.basename(filepath)}:")
        for f_val in sorted(list(set(found))):
            print(f"  {f_val}")
