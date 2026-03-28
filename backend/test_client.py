import json
from app import app

# Create a test client
client = app.test_client()

print("Testing POST to /api/chat/recipe")
response = client.post('/api/chat/recipe', 
                       data=json.dumps({"message": "I want to make a sandwich"}),
                       content_type='application/json')
print(f"Status Code: {response.status_code}")
print(f"Data: {response.data.decode('utf-8')}")

print("\Testing POST to /api/chat/ping")
response = client.post('/api/chat/ping')
print(f"Status Code: {response.status_code}")
print(f"Data: {response.data.decode('utf-8')}")
