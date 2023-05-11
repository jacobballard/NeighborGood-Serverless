#!/usr/bin/env python3
import json
import requests
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('/Users/jacobballard/Desktop/NeighborGood/Serverless/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')
firebase_admin.initialize_app(cred)

uid = "IFbVdElb05U8xWMkKKrviPO7foK2"
custom_token = auth.create_custom_token(uid)
print(custom_token)

url = 'http://localhost:8080/create_store'  # Replace with your actual endpoint
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + custom_token.decode('utf-8'),
}
data = {
    # 'id': "12345abcd",
    # "jwt" : custom_token,
    'title': 'Sample Store',
    'description': 'This is a sample store.',
    'instagram': 'sample_store_instagram',
    'tiktok': 'sample_store_tiktok',
    'facebook': 'sample_store_facebook',
    'latitude': 12.34,
    'longitude': 56.78,
    'delivery_radius': 10,
    'delivery_methods': ["local pickup", "delivery"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f'Status code: {response.status_code}')
print(f'Response: {response.text}')

