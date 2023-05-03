import json
import requests

url = "http://localhost:5000/create_product"  # Replace with your actual endpoint
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your_token_here"
}
data = {
    "title": "Test Product",
    "description": "This is a test product.",
    "price": 9.99,
    "stock" : 1,
    "allow_shipping": True,
    "allow_local_pickup": False,
    "allow_delivery": False
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")
