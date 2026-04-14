import os

filepath = os.path.join(os.path.dirname(__file__), 'app.py')

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"rssi": loc.get("rssi", 0),',
                          '"rssi": loc.get("raw_rssi", 0),\n                "smoothed_rssi": loc.get("smoothed_rssi", 0),')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Keys fixed")
