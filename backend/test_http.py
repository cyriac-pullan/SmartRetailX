import urllib.request
import json
import urllib.error

url = 'http://127.0.0.1:5000/api/chat/recipe'
data = json.dumps({'message': 'I want to make a sandwich'}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    response = urllib.request.urlopen(req)
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTPError Body:")
    print(e.read().decode())
