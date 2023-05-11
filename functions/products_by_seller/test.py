import firebase_admin
from firebase_admin import auth, firestore, credentials
import functions_framework
from sqlalchemy import create_engine, text
import flask

db_user = 'postgres'
db_pass = 'postgres'
db_name = 'postgres'
db_host = 'localhost'
db_port = '5432'

connection_string = f'postgresql://jacobballard@{db_host}/{db_name}'
db = create_engine(f"postgresql://jacobballard@localhost/postgres")

@functions_framework.http
def products_by_seller(request: flask.Request):
    if request.method == 'POST':
        request_data = request.get_json()
        seller_id = request_data.get('seller_id')

        if not seller_id:
            return {'error': 'Required field: seller_id'}, 400

        connection = db.connect()

        try:
            get_products_query = text(
                'SELECT * FROM products '
                'WHERE seller_id = :seller_id'
            )
            products = connection.execute(get_products_query, {'seller_id': seller_id}).fetchall()

            products_list = []

            for product in products:
                product_dict = {
                    'id': product.id,
                    'title': product.title,
                    'description': product.description,
                    'price': product.price,
                    'stock': product.stock,
                    'seller_id': product.seller_id
                }
                products_list.append(product_dict)

            return {'products': products_list}, 200
        except Exception as e:
            connection.close()
            return {'error': str(e)}, 500
    else:
        return {'error': 'Invalid request method'}, 405
