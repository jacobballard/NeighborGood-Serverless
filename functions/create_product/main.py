import flask
import functions_framework
from sqlalchemy import create_engine, text
from shared.sql_db import db as sql_db
from shared.firestore_db import db as firestore_db
from shared.auth import is_authenticated_wrapper, has_required_role, headers

@is_authenticated_wrapper(False)
@has_required_role("seller")
@functions_framework.http
def create_product(request: flask.Request):
    if request.method == 'POST':
        user = flask.g.user
        seller_id = user['user_id']
        request_data = request.get_json()
        print(request_data)
        id = request_data.get('id')
        title = request_data.get('title')
        description = request_data.get('description', None)
        price = float(request_data.get('price'))
        # stock = request_data.get('stock', None)
        # allow_shipping = request_data.get('allow_shipping', False)
        # allow_local_pickup = request_data.get('allow_local_pickup', False)
        # allow_delivery = request_data.get('allow_delivery', False)
        delivery_methods = request_data.get('delivery_methods', [])
        print("delivery methods")
        print(delivery_methods)
        product_modifiers = request_data.get('modifiers', [])
        print(delivery_methods)
        print(product_modifiers)
        # Convert the delivery methods to the new format
        new_delivery_methods = []
        # for method in delivery_methods:
        #     method_type = method["type"]
        #     if method_type == 'Local pickup':
        #         insert_delivery_methods_query = text(
        #             'INSERT INTO product_delivery_methods (product_id, delivery_method_id) '
        #             'VALUES (:product_id, :method)'
        #         )
        #         connection.execute(insert_delivery_methods_query, {'product_id': id, 'method': 1})
        #     elif method_type == 'Delivery':
        #         try:
        #             int(method['range'])
        #             print(method['range'])
        #             print("range")
        #         except ValueError:
        #             return False
        #     else:
        #         insert_delivery_methods_query = text(
        #             'INSERT INTO product_delivery_methods (product_id, delivery_method_id) '
        #             'VALUES (:product_id, :method)'
        #         )
        #         connection.execute(insert_delivery_methods_query, {'product_id': id, 'method': 2})

        if not (title and price):
            return {'error': 'Required fields: title, price'}, 400

        if not isinstance(price, (int, float)):
            return {'error': 'Price must be a numerical value'}, 400

        # if stock is not None and not isinstance(stock, int):
        #     return {'error': 'Stock must be an integer value'}, 400

        # if len(new_delivery_methods) == 0:
        #     return {'error': 'Must have at least one delivery method'}, 400

        insert_product_query = text(
            'INSERT INTO products (id, title,  price,  seller_id) '
            'VALUES (:id, :title, :price, :seller_id) '
            
        )

        # print("here")

        product_values = {
            'id' : id,
            'title': title,
            'price': price,
            'seller_id': seller_id,
        }

        connection = sql_db.connect()
        print("connected")

        try:
            result = connection.execute(insert_product_query, product_values)
            print("result")
            # product_id = result.fetchone()[0]


            # for method in new_delivery_methods:
            #     insert_delivery_methods_query = text(
            #         'INSERT INTO product_delivery_methods (product_id, delivery_method_id) '
            #         'VALUES (:product_id, :method)'
            #     )
            #     connection.execute(insert_delivery_methods_query, {'product_id': product_id, 'method': method})
            for method in delivery_methods:
                
                method_type = method["type"]
                print("method_type")
                if method_type == 'Local pickup':
                    insert_delivery_methods_query = text(
                        'INSERT INTO product_delivery_method (product_id, delivery_method_id) '
                        'VALUES (:product_id, :method)'
                    )
                    connection.execute(insert_delivery_methods_query, {'product_id': id, 'method': 1})
                    print("executed")
                elif method_type == 'Delivery':
                    insert_delivery_methods_query = text(
                        'INSERT INTO product_delivery_method (product_id, delivery_method_id, delivery_range) '
                        'VALUES (:product_id, :method, :range)'
                    )
                    connection.execute(insert_delivery_methods_query, {'product_id': id, 'method': 3, 'range' : int(method['range'])})
                else:
                    insert_delivery_methods_query = text(
                        'INSERT INTO product_delivery_method (product_id, delivery_method_id) '
                        'VALUES (:product_id, :method)'
                    )
                    connection.execute(insert_delivery_methods_query, {'product_id': id, 'method': 2})
            # for mod in product_modifiers:
            #     modifier_type = mod['modifier_type']
            #     name = mod['name']
            #     max_options = mod.get('max_options')
            #     max_characters = mod.get('max_characters')
            #     options = mod.get('options', [])
            #     required = mod.get('required', True)

            #     insert_modifier_query = text(
            #         'INSERT INTO modifiers (name, modifier_type, max_options, modifier_required, max_characters) '
            #         'VALUES (:name, :modifier_type, :max_options, :modifier_required, :max_characters) '
            #         'RETURNING id'
            #     )

            #     modifier_values = {
            #         'name': name,
            #         'modifier_type': modifier_type,
            #         'max_options': max_options,
            #         'modifier_required' : required,
            #         'max_characters': max_characters,
            #     }

            #     result = connection.execute(insert_modifier_query, modifier_values)
            #     modifier_id = result.fetchone()[0]
            #     # TODO : All of this needs to be null safe and return errors if lacking a necessary
            #     # logical piece
            #     if modifier_type == 'choice':
            #         for option in options:
            #             opt_name = option['name']
            #             opt_price = option.get('price')

            #         insert_option_query = text(
            #             'INSERT INTO modifier_details (modifier_id, name, price) '
            #             'VALUES (:modifier_id, :opt_name, :opt_price) '
            #         )

            #         option_values = {
            #             'modifier_id': modifier_id,
            #             'opt_name': opt_name,
            #             'opt_price': opt_price,
            #         }

            #         connection.execute(insert_option_query, option_values)

            # insert_product_modifier_query = text(
            #     'INSERT INTO product_modifiers (product_id, modifier_id) '
            #     'VALUES (:product_id, :modifier_id)'
            # )

            # product_modifier_values = {
            #     'product_id': product_id,
            #     'modifier_id': modifier_id,
            # }

            # connection.execute(insert_product_modifier_query, product_modifier_values)
            # if 'image_urls' in request_data:
            #     image_urls = request_data.get('image_urls')
            #     if isinstance(image_urls, list):
            #         for image_url in image_urls:
            #             insert_image_query = text(
            #                 'INSERT INTO product_images (product_id, image_url) VALUES (:product_id, :image_url)'
            #             )
            #             connection.execute(insert_image_query, {"product_id" : product_id, "image_url" : image_url})
            connection.commit()
            connection.close()

            # return {'success': 'Product created successfully'}, 200

        except Exception as e:
            print(e)
            connection.close()
            return {'error': str(e)}, 500
        
        try:
            doc_ref = firestore_db.collection(u'users').document(seller_id).collection(u'products').document(id)

            doc_ref.set({
                u'title' : title,
                u'description' : description,
                u'price' : int(price),
                u'delivery_methods' : delivery_methods,
                u'modifiers' : product_modifiers
            }, merge = True)
        except:
            pass
        
        return ('', 204, headers)

    else:
        return {'error': 'Invalid request method'}, 405

