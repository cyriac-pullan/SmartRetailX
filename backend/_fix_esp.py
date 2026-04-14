import os

filepath = os.path.join(os.path.dirname(__file__), 'app.py')

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the esp-status endpoint
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'esp-status' in line and 'app.route' in line:
        start_idx = i
        break

if start_idx is None:
    print("ERROR: Could not find esp-status endpoint")
    exit(1)

# Find the end - next @app.route
for i in range(start_idx + 2, len(lines)):
    stripped = lines[i].strip()
    if '@app.route' in stripped:
        end_idx = i
        break

print(f"Replacing lines {start_idx+1} to {end_idx} (1-indexed)")

new_code = """\
@app.route('/api/nav/esp-status', methods=['GET'])
def get_esp_status():
    \"\"\"Return live position from background BLE scanner.\"\"\"
    # Read from background service (avoids BLE adapter conflict)
    if smart_cart_service:
        loc = getattr(smart_cart_service, 'current_location', None)
        if loc and loc.get("partition"):
            corridor_id = loc.get("corridor", "")
            partition = loc.get("partition", "")
            corridor_labels = {"L": "Corr-L", "12": "Corr-A1A2", "23": "Corr-A2A3", "R": "Corr-R"}
            label = corridor_labels.get(corridor_id, "")
            return jsonify({
                "position": f"{partition} ({label})" if label else partition,
                "corridor": corridor_id,
                "partition": partition,
                "esp": loc.get("esp", ""),
                "rssi": loc.get("rssi", 0),
            })
    return jsonify({"position": "Scanning..."})

"""

new_lines = [l + '\r\n' for l in new_code.split('\n')]
lines[start_idx:end_idx] = new_lines

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("SUCCESS: esp-status reverted to background service (no BLE conflict)!")
