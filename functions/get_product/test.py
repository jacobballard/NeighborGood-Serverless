#!/usr/bin/env python3
import json
import requests
from sqlalchemy import create_engine, text

url = 'http://localhost:8080/get_product'  # Replace with your actual endpoint
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your_token_here'
}
data = {
    'id' : "19e9669e-cb27-40e7-bd7a-0e322ae83c38"
}


response = requests.post(url, headers=headers, data=json.dumps(data))

print(f'Status code: {response.status_code}')
print(f'Response: {response.text}')

