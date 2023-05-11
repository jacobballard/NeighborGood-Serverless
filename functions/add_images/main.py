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
db = create_engine(connection_string)

@functions_framework.http
def add_images(request: flask.Request):
    if request.method == 'POST':
        # TODO: Add authentication with JWT as needed

        request_data = request.get_json()
        request_type = request_data.get('request_type')
        id = request_data.get('product_id')
        image_urls = request_data.get('image_urls')

        if not (product_id and image_urls):
            return {'error': 'Required fields: id, image_urls'}, 400

        if not isinstance(image_urls, list):
            return {'error': 'image_urls must be a list'}, 400

        connection = db.connect()

        query = ""
        item = ""
        if request_type == "seller":
            query = 'INSERT INTO seller_images (seller_id, image_url)'
            item = 'seller'
        else:
            query = 'INSERT INTO product_images (product_id, image_url) '
            item = 'product'

        try:
            for image_url in image_urls:
                insert_image_query = text(
                     query +
                    'VALUES (:id, :image_url)'
                )
                connection.execute(insert_image_query, {"id" : id, "image_url" : image_url})
            return {'success': f'Image URLs for {item} {id} inserted successfully'}, 200
        except Exception as e:
            connection.close()
            return {'error': str(e)}, 500
    else:
        return {'error': 'Invalid request method'}, 405
