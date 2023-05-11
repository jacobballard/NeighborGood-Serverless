# import firebase_admin
# from firebase_admin import auth, firestore, credentials
# import functions_framework
# from sqlalchemy import create_engine, text
# import flask



# # cred = credentials.Certificate("../pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json")
# # firebase_admin.initialize_app(cred)


# db_user = 'postgres'
# db_pass = 'postgres'
# db_name = 'postgres'
# db_host = 'localhost'
# db_port = '5432'

# connection_string = f'postgresql://jacobballard@{db_host}/{db_name}'
# db = create_engine(f"postgresql://jacobballard@localhost/postgres")

# @functions_framework.http
# def create_product(request: flask.Request):
#     if request.method == 'POST':
#         # TODO : Make empty string and handle with jwt.
#         uid = "Seller1"
#         ## Get the token from the request header
#         # token = request.headers.get('Authorization')
#         # if not token:
#         #     return {'error': 'No token provided'}, 401

#         # try:
#         #     # Verify the token and get the user's information
#         #     user = auth.verify_id_token(token)
#         #     uid = user['uid']
#         #     # Check the user's role in Firestore
#         #     db_firestore = firestore.client()
#         #     user_ref = db_firestore.collection('users').document(user['uid'])
#         #     user_data = user_ref.get().to_dict()
#         #     if not user_data or user_data.get('role') != 'seller':
#         #         return {'error': 'Unauthorized'}, 403
#         # except ValueError:
#         #     return {'error': 'Invalid token'}, 401
#         # except auth.AuthError:
#         #     return {'error': 'Invalid token'}, 401

#         request_data = request.get_json()
#         title = request_data.get('title')
#         description = request_data.get('description')
#         price = request_data.get('price')
#         stock = request_data.get('stock')
#         allow_shipping = request_data.get('allow_shipping')
#         allow_local_pickup = request_data.get('allow_local_pickup')
#         allow_delivery = request_data.get('allow_delivery')
#         seller_id = uid
#         delivery_methods = []
#         product_modifiers = request_data.get('product_modifiers')

        
#         if allow_local_pickup:
#             delivery_methods.append(1)
        
#         if allow_delivery:
#             delivery_methods.append(2)
        
#         if allow_shipping:
#             delivery_methods.append(3)

#         if len(delivery_methods) == 0:
#             return {'error': 'Must have at least one delivery method'}, 400
        

#         if not (title and price):
#             return {'error': 'Required fields: title, price'}, 400
        
#         if not isinstance(price, (int, float)):
#             return {'error': 'Price must be a numerical value'}, 400

#         if stock is not None and not isinstance(stock, int):
#             return {'error': 'Stock must be an integer value'}, 400
        

#         connection = db.connect()
        
#         # Lol I think this monstrosity uses a transaction that
#         # works when the try succeeds but I should really test this more
#         try:
#             with connection.begin():
#                 insert_product_query = text(
#                     'INSERT INTO products (title, description, price, stock, seller_id) '
#                     'VALUES (:title, :description, :price, :stock, :seller_id) '
#                     'RETURNING id'
#                 )
#                 product_values = {'title': title, 'description': description, 'price': price, 'stock': stock, 'seller_id': seller_id}
#                 result = connection.execute(insert_product_query, product_values)
                
#                 product_id = result.fetchone()[0]
                

#                 for method in delivery_methods:
#                     insert_delivery_methods_query = text(
#                         'INSERT INTO product_delivery_methods (product_id, delivery_method_id) '
#                         'VALUES (:product_id, :method)'
#                     )
#                     connection.execute(insert_delivery_methods_query, {'product_id': product_id, 'method': method})
                
#                 for mod in product_modifiers:
#                     modifier_type = mod["modifier_type"]
#                     if modifier_type == "choice":
#                         name = mod["name"]
#                         max_options = mod["max_options"]
#                         insert_product_mod_query = text(
#                             'INSERT INTO modifiers (name, modifier_type, max_options) '
#                             'VALUES (:name, :modifier_type, :max_options) '
#                             'RETURNING id'
#                         )
#                         mod_id = connection.execute(insert_product_mod_query, {'name' : name, 'modifier_type' : modifier_type,'max_options' : max_options})
#                         mod_id = mod_id.fetchone()[0]
                        
                        
                            
#                         insert_prod_mod_query = text(
#                             'INSERT INTO product_modifiers (product_id, modifier_id) '
#                             'VALUES (:product_id, :mod_id)'
#                         )

#                         connection.execute(insert_prod_mod_query, {"product_id" : product_id, "mod_id" : mod_id})

#                         options = mod["options"]
#                         for option in options:
#                             opt_name = option['name']
#                             opt_price = None
#                             if 'price' in option:
#                                 opt_price = option[price]
                            
#                             insert_mod_option_query = None

                            
#                             insert_mod_option_query = text(
#                                 'INSERT INTO modifier_details (modifier_id, name, price) '
#                                 'VALUES (:mod_id, :opt_name, :opt_price)'
#                                 'RETURNING id'
#                             )

#                             connection.execute(insert_mod_option_query, {'mod_id' : mod_id, "opt_name" : opt_name, "opt_price" : opt_price})

#                     elif mod["modifier_type"] == "input":
#                         name = mod["name"]
#                         max_characters = mod["max_characters"]

#                         insert_input_mod_query = text(
#                             'INSERT INTO modifiers (name, modifier_type, max_options, max_characters) '
#                             'VALUES (:name, :modifier_type, :max_options, :max_characters)'
#                             'RETURNING id'
#                         )

#                         mod_id = connection.execute(insert_input_mod_query, {'name' : name, 'modifier_type' : modifier_type, 'max_options' : None, 'max_characters' : max_characters })
#                         mod_id = mod_id.fetchone()[0]
#                         insert_prod_mod_query = text(
#                             'INSERT INTO product_modifiers (product_id, modifier_id) '
#                             'VALUES (:product_id, :mod_id)'
#                         )

#                         connection.execute(insert_prod_mod_query, {"product_id" : product_id, "mod_id" : mod_id})
#             # connection.commit()
#             # Commmit 
#             return {'success': 'Product created successfully'}, 200
#         except Exception as e:
#             # Rollback
#             connection.close()
#             return {'error': str(e)}, 500
#     else:
#         return {'error': 'Invalid request method'}, 405

import flask
import functions_framework
from sqlalchemy import create_engine, text
from functions.shared.sql_db import db
from functions.shared.auth import is_authenticated_wrapper, has_required_role

@is_authenticated_wrapper(False)
@has_required_role("seller")
@functions_framework.http
def create_product(request: flask.Request):
    if request.method == 'POST':
        seller_id = flask.g.user['uid']
        request_data = request.get_json()
        title = request_data.get('title')
        description = request_data.get('description', None)
        price = request_data.get('price')
        stock = request_data.get('stock', None)
        # allow_shipping = request_data.get('allow_shipping', False)
        # allow_local_pickup = request_data.get('allow_local_pickup', False)
        # allow_delivery = request_data.get('allow_delivery', False)
        delivery_methods = request_data.get('delivery_methods', [])
        product_modifiers = request_data.get('product_modifiers', [])

        # Convert the delivery methods to the new format
        new_delivery_methods = []
        for method in delivery_methods:
            if method == 'Local Pickup':
                new_delivery_methods.append(1)
            elif method == 'Delivery':
                new_delivery_methods.append(2)
            else:
                new_delivery_methods.append(3)

        if not (title and price):
            return {'error': 'Required fields: title, price'}, 400

        if not isinstance(price, (int, float)):
            return {'error': 'Price must be a numerical value'}, 400

        if stock is not None and not isinstance(stock, int):
            return {'error': 'Stock must be an integer value'}, 400

        if len(new_delivery_methods) == 0:
            return {'error': 'Must have at least one delivery method'}, 400

        insert_product_query = text(
            'INSERT INTO products (title, description, price, stock, seller_id) '
            'VALUES (:title, :description, :price, :stock, :seller_id) '
            'RETURNING id'
        )

        product_values = {
            'title': title,
            'description': description,
            'price': price,
            'stock': stock,
            'seller_id': seller_id,
        }

        connection = db.connect()

        try:
            result = connection.execute(insert_product_query, product_values)
            product_id = result.fetchone()[0]

            for method in new_delivery_methods:
                insert_delivery_methods_query = text(
                    'INSERT INTO product_delivery_methods (product_id, delivery_method_id) '
                    'VALUES (:product_id, :method)'
                )
                connection.execute(insert_delivery_methods_query, {'product_id': product_id, 'method': method})

            for mod in product_modifiers:
                modifier_type = mod['modifier_type']
                name = mod['name']
                max_options = mod.get('max_options')
                max_characters = mod.get('max_characters')
                options = mod.get('options', [])

                insert_modifier_query = text(
                    'INSERT INTO modifiers (name, modifier_type, max_options, max_characters) '
                    'VALUES (:name, :modifier_type, :max_options, :max_characters) '
                    'RETURNING id'
                )

                modifier_values = {
                    'name': name,
                    'modifier_type': modifier_type,
                    'max_options': max_options,
                    'max_characters': max_characters,
                }

                result = connection.execute(insert_modifier_query, modifier_values)
                modifier_id = result.fetchone()[0]

                if modifier_type == 'choice':
                    for option in options:
                        opt_name = option['name']
                        opt_price = option.get('price')

                    insert_option_query = text(
                        'INSERT INTO modifier_details (modifier_id, name, price) '
                        'VALUES (:modifier_id, :opt_name, :opt_price) '
                    )

                    option_values = {
                        'modifier_id': modifier_id,
                        'opt_name': opt_name,
                        'opt_price': opt_price,
                    }

                    connection.execute(insert_option_query, option_values)

            insert_product_modifier_query = text(
                'INSERT INTO product_modifiers (product_id, modifier_id) '
                'VALUES (:product_id, :modifier_id)'
            )

            product_modifier_values = {
                'product_id': product_id,
                'modifier_id': modifier_id,
            }

            connection.execute(insert_product_modifier_query, product_modifier_values)

            connection.commit()
            connection.close()

            return {'success': 'Product created successfully'}, 200

        except Exception as e:
            connection.close()
            return {'error': str(e)}, 500

    else:
        return {'error': 'Invalid request method'}, 405

