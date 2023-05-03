import firebase_admin
from firebase_admin import auth, firestore, credentials
import functions_framework
from sqlalchemy import create_engine
from google.cloud import storage

cred = credentials.Certificate("path/to/your/firebase-service-account-key.json")
firebase_admin.initialize_app(cred)


db_user = 'postgres'
db_pass = 'postgres'
db_name = 'postgres'
db_host = 'localhost'
db_port = '5432'

connection_string = f'postgresql://@{db_host}/{db_name}'
db = create_engine(connection_string)

@functions_framework.http
def create_product(request: flask.Request):
    if request.method == 'POST':
        uid = ""
        ## Get the token from the request header
        # token = request.headers.get('Authorization')
        # if not token:
        #     return {'error': 'No token provided'}, 401

        # try:
        #     # Verify the token and get the user's information
        #     user = auth.verify_id_token(token)
        #     uid = user['uid']
        #     # Check the user's role in Firestore
        #     db_firestore = firestore.client()
        #     user_ref = db_firestore.collection('users').document(user['uid'])
        #     user_data = user_ref.get().to_dict()
        #     if not user_data or user_data.get('role') != 'seller':
        #         return {'error': 'Unauthorized'}, 403
        # except ValueError:
        #     return {'error': 'Invalid token'}, 401
        # except auth.AuthError:
        #     return {'error': 'Invalid token'}, 401

        request_data = request.get_json()
        title = request_data.get('title')
        description = request_data.get('description', None)
        price = request_data.get('price')
        stock = request_data.get('stock', None)
        seller_id = uid
        delivery_methods = request_data.get('delivery_methods', [])

        if not (title and pric):
            return {'error': 'Required fields: title, price'}, 400
        
        if not isinstance(price, (int, float)):
            return {'error': 'Price must be a numerical value'}, 400

        if stock is not None and not isinstance(stock, int):
            return {'error': 'Stock must be an integer value'}, 400

        connection = db.connect()

        try:
            insert_product_query = f"""
                INSERT INTO products (id, title, description, price, stock, seller_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            product_values = (product_id, title, description, price, stock, seller_id)
            connection.execute(insert_product_query, product_values)

            for method in delivery_methods:
                insert_delivery_methods_query = f"""
                    INSERT INTO product_delivery_methods (product_id, delivery_method_id)
                    VALUES (%s, %s)
                """
                connection.execute(insert_delivery_methods_query, (product_id, method))

            connection.commit()
            connection.close()

            return {'success': 'Product created successfully'}, 200

        except Exception as e:
            connection.close()
            return {'error': str(e)}, 500

    else:
        return {'error': 'Invalid request method'}, 405
