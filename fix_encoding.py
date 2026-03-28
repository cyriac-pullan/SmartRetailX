"""Fix double-encoded UTF-8 in billing.html caused by PowerShell truncation."""
path = r'..\frontend\billing.html'

with open(path, 'rb') as f:
    raw = f.read()

# Strip BOM
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]

# The file is valid UTF-8 but the *content* was garbled:
# PowerShell read it as Latin-1 then wrote back those bytes as UTF-8 codepoints.
# Fix: decode as UTF-8, then re-encode as Latin-1, then decode as UTF-8.
text = raw.decode('utf-8')
fixed = text.encode('latin-1').decode('utf-8')

with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(fixed)

print('Done!')
for ch in ['₹', '🛒', '−', '✕', '💳', '🗑️', '😊', '🎉']:
    print(f'  {ch!r}: {"OK" if ch in fixed else "MISSING"}')
