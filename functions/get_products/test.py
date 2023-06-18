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
    'filter_pickup': True,
    'filter_delivery': False,
    'filter_shipping': False,
    'lat': 40.730610,  # Replace with the actual latitude
    'lng': -73.935242,  # Replace with the actual longitude
    'radius': 5  # Replace with the actual radius
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f'Status code: {response.status_code}')
print(f'Response: {response.text}')
