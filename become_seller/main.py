from sqlalchemy import create_engine
import flask
import functions_framework
import os

db_user = 'postgres'
db_pass = 'postgres'
db_name = 'postgres'
db_host = 'localhost'
db_port = '5432'

connection_string = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
db = create_engine(connection_string)

@functions_framework.http
def create_store(request: flask.Request):
    if request.method == 'POST':
        request_data = request.args.to_dict()

        id = request_data.get('id')
        title = request_data.get('title')
        description = request_data.get('description', None)
        latitude = request_data.get('latitude')
        longitude = request_data.get('longitude')
        instagram = request_data.get('instagram', None)
        tiktok = request_data.get('tiktok', None)
        pinterest = request_data.get('pinterest', None)
        facebook = request_data.get('facebook', None)
        delivery_methods = request_data.get('delivery_methods', [])

        if not (id and title and latitude and longitude):
            return {'error': 'Required fields: id, title, latitude, and longitude'}, 400

        insert_seller_query = f"""
            INSERT INTO sellers (id, title, description, lat, lng, instagram, tiktok, pinterest, facebook)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        seller_values = (id, title, description, latitude, longitude, instagram, tiktok, pinterest, facebook)

        connection = db.connect()

        try:
            connection.execute(insert_seller_query, seller_values)

            for method in delivery_methods:
                insert_delivery_methods_query = f"""
                    INSERT INTO seller_delivery_methods (seller_id, delivery_method_id)
                    VALUES (%s, %s)
                """
                connection.execute(insert_delivery_methods_query, (id, method))

            connection.commit()
            connection.close()

            return {'success': 'Store created successfully'}, 200

        except Exception as e:
            connection.close()
            return {'error': str(e)}, 500
    else:
        return {'error': 'Invalid request method'}, 405
