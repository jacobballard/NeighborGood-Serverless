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
    'address_line_1': "2354 Randolph Ct",
    'address_line_2' : "",
    'zip_code': '40503',
    'city' : 'Lexington',
    'state' : 'KY',
    'delivery_methods': {
        'local_pickup' : {
            'show_address_to_customers' : False,
        },
        'delivery' : {
            'range' : 25.0,
            'fee' : 5.0,
        },
        'shipping' : {
            'fee' : 10.0,
            'eta' : 14,
        } 
    },
    'image_urls' : ["http://placeholder.io/image", "etc", "etc"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f'Status code: {response.status_code}')
print(f'Response: {response.text}')

