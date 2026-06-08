with open('api/routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '/outcome' in line:
        print(f"Match on line {i+1}:")
        start = max(0, i-5)
        end = min(len(lines), i+30)
        for idx in range(start, end):
            print(f"{idx+1}: {lines[idx]}", end="")
        print("-" * 50)
