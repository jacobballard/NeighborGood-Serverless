import firebase_admin
import functions_framework
from sqlalchemy import create_engine, text
import flask
from shared import database

# cred = credentials.Certificate("../pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json")
# firebase_admin.initialize_app(cred)


@functions_framework.http
def get_product(request: flask.Request):
    # Do I need to do firebase auth here? Probably

    request_data = request.get_json()
    id = request_data.get('id')

    connection = database.db.connect()

    # Get product data
    product_query = text('SELECT * FROM products WHERE id = :id')
    product_data = connection.execute(product_query, {'id': id}).fetchone()
    # product_data = row2dict(connection.execute(product_query, {'id': id}).fetchone())
    print(product_data)
    print('data')
    if not product_data:
        connection.close()
        return {'error': 'Product not found'}, 404
    
    id, name, description, price, stock, seller_id = product_data

    # Get product images
    images_query = text('SELECT image_url FROM product_images WHERE product_id = :id')
    images_data = connection.execute(images_query, {'id': id}).fetchall()
    images = [row[0] for row in images_data]

    # Get product delivery methods
    delivery_methods_query = text(
        'SELECT dm.id, dm.method_name FROM product_delivery_methods pdm '
        'JOIN delivery_methods dm ON pdm.delivery_method_id = dm.id '
        'WHERE pdm.product_id = :id'
    )
    delivery_methods_data = connection.execute(delivery_methods_query, {'id': id}).fetchall()
    # delivery_methods = [dict(zip(['id', 'name'], row)) for row in delivery_methods_data]
    delivery_methods = [row[1] for row in delivery_methods_data]
    print("DM")
    print(delivery_methods)

    # Get product modifiers
    modifiers_query = text(
        'SELECT m.* FROM product_modifiers pm '
        'JOIN modifiers m ON pm.modifier_id = m.id '
        'WHERE pm.product_id = :id'
    )
    modifiers_data = connection.execute(modifiers_query, {'id': id}).fetchall()
    modifiers = [dict(zip(['id', 'name', 'modifier_type', 'max_options', 'max_characters'], row)) for row in modifiers_data]
    print(modifiers)
    print("modifiers ^^^")
    # Get modifier_details for each modifier
    for modifier in modifiers:
        if modifier['modifier_type'] == 'choice':
            details_query = text('SELECT name, price FROM modifier_details WHERE modifier_id = :modifier_id')
            details_data = connection.execute(details_query, {'modifier_id': modifier['id']}).fetchall()
            modifier.pop('max_characters', None)
            modifier['options'] = [dict(zip(['name', 'price'], row)) for row in details_data]
        elif modifier['modifier_type'] == 'input':
            modifier.pop('max_options', None)
        modifier.pop('id', None)

    connection.close()

    for item in product_data:
        print(item)
        print("tem")

    # print(product_data['title'])
    # print("was pd")
    # print(str(images) + "images")
    # print(delivery_methods + " dm")

    # Build JSON response
    product_json = {
        'title': name,
        'description': description,
        'price': price,
        'stock': stock,
        'images': images,
        'delivery_methods': delivery_methods,
        'product_modifiers': modifiers
    }

    return product_json, 200
