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
                required = mod.get('required', True)

                insert_modifier_query = text(
                    'INSERT INTO modifiers (name, modifier_type, max_options, modifier_required, max_characters) '
                    'VALUES (:name, :modifier_type, :max_options, :modifier_required, :max_characters) '
                    'RETURNING id'
                )

                modifier_values = {
                    'name': name,
                    'modifier_type': modifier_type,
                    'max_options': max_options,
                    'modifier_required' : required,
                    'max_characters': max_characters,
                }

                result = connection.execute(insert_modifier_query, modifier_values)
                modifier_id = result.fetchone()[0]
                # TODO : All of this needs to be null safe and return errors if lacking a necessary
                # logical piece
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
            if 'image_urls' in request_data:
                image_urls = request_data.get('image_urls')
                if isinstance(image_urls, list):
                    for image_url in image_urls:
                        insert_image_query = text(
                            'INSERT INTO product_images (product_id, image_url) VALUES (:product_id, :image_url)'
                        )
                        connection.execute(insert_image_query, {"product_id" : product_id, "image_url" : image_url})
            connection.commit()
            connection.close()

            return {'success': 'Product created successfully'}, 200

        except Exception as e:
            connection.close()
            return {'error': str(e)}, 500

    else:
        return {'error': 'Invalid request method'}, 405

