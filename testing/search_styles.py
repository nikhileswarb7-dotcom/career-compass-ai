import re

with open("frontend-backup/roadmap.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find the style tag contents
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if style_match:
    styles = style_match.group(1)
    
    # Extract rules for key classes
    classes = [".coach-panel", ".chatbot-drawer", ".layout-grid", ".sidebar", ".hub-grid"]
    for c in classes:
        print(f"--- Style for {c} ---")
        pattern = re.escape(c) + r"\s*\{(.*?)\}"
        matches = re.findall(pattern, styles, re.DOTALL)
        for m in matches:
            print(m.strip())
else:
    print("No style tag found.")
