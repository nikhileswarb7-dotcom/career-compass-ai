import re

with open("frontend-backup/roadmap.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find all div classes
div_classes = re.findall(r'class="([^"]+)"', content)
unique_classes = sorted(list(set(div_classes)))

print("Unique Classes:")
for c in unique_classes:
    if "grid" in c or "col" in c or "side" in c or "panel" in c or "coach" in c or "chat" in c:
        print(f"  {c}")

# Search for the word "coach" or "chat" structure
print("\nCoach/Chat elements:")
for line in content.split("\n"):
    if "id=\"coach" in line or "class=\"coach" in line or "id=\"chat" in line or "class=\"chat" in line:
        clean = line.strip().encode('ascii', 'ignore').decode('ascii')
        print(f"  {clean}")
