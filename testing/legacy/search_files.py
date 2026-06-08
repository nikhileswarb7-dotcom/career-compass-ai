import os

def search_files(directory, term):
    results = []
    for root, dirs, files in os.walk(directory):
        if '.venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py') or file.endswith('.sql') or file.endswith('.json') or file.endswith('.jsx') or file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for idx, line in enumerate(f):
                            if term in line:
                                results.append(f"{filepath}:{idx+1}: {line.strip()}")
                except Exception:
                    pass
    return results

print("SEARCH FOR student_outcomes:")
for r in search_files('.', 'student_outcomes'):
    print(r)

print("\nSEARCH FOR users:")
for r in search_files('.', 'users'):
    print(r)
