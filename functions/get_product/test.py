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
    'id' : "3b5dd70f-3cb5-48f9-8fb7-7e569ded9405"
}


response = requests.post(url, headers=headers, data=json.dumps(data))

print(f'Status code: {response.status_code}')
print(f'Response: {response.text}')

