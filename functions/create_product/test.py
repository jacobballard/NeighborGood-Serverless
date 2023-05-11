#!/usr/bin/env python3
import json
import requests
from sqlalchemy import create_engine, text

url = 'http://localhost:8080/create_product'  # Replace with your actual endpoint
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your_token_here'
}
data = {
    'title': 'Test Product',
    'description': 'This is a test product.',
    'price': 9.99,
    'stock' : 1,
    'allow_shipping': False,
    'allow_local_pickup': True,
    'allow_delivery': True,
    'product_modifiers' : 
    [
        {
            "modifier_type" : "choice",
            "name" : "Choose a color",
            "max_options" : 1,
            "options" : 
            [
                {
                    "name" : "Blue"
                    # "price" : 0.99

                },
                {
                    "name" : "Red"
                },
                {
                    "name" : "Green"
                }
            ]
        },
        {
            "modifier_type" : "input",
            "name" : "Write your initials",
            "max_characters" : 10
        }
    ]
}
# engine = create_engine(f'postgresql://jacobballard@localhost/postgres')
# with engine.connect() as connection:
#     # test = connection.execute(text(('WITH inserted AS ('
#     # 'INSERT INTO products(title, description, price, stock, seller_id)'
#     # "VALUES ('Product 3', 'doggy', 5.5, 1, 'Seller1')"
#     # 'RETURNING id'
#     # ')'
#     # # )))

#     # 'INSERT INTO product_delivery_methods(product_id, delivery_method_id)'
#     # 'SELECT inserted.id, 1 FROM inserted;')))
#     # connection.commit()

#     test = connection.execute(text("SELECT * FROM products;"))
#     connection.commit()
#     print(test)

response = requests.post(url, headers=headers, data=json.dumps(data))

print(f'Status code: {response.status_code}')
print(f'Response: {response.text}')

