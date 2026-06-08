with open('backend/api/parse_profiles.py', 'r', encoding='utf-8') as f:
    backend_content = f.read()

with open('database/parse_profiles.py', 'r', encoding='utf-8') as f:
    database_content = f.read()

print("Are parse_profiles.py identical?", backend_content == database_content)
print("Lengths:", len(backend_content), len(database_content))
