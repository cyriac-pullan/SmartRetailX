import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- SEARCH RESULTS ---")
for i, line in enumerate(lines):
    if '/api/chat/recipe' in line or 'chat_recipe_finder' in line:
        print(f"Line {i+1}: {line.strip()}")
