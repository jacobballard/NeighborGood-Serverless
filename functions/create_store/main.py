from sqlalchemy import create_engine, text
import flask
import functions_framework
import os
# from ...shared import database
# from ...shared.sql_db import db
# from ...shared.auth import is_authenticated_wrapper, has_required_role
from functions.shared.sql_db import db
from functions.shared.auth import is_authenticated_wrapper, has_required_role


@is_authenticated_wrapper(False)
@has_required_role("buyer")
@functions_framework.http
def create_store(request: flask.Request):

    print("then create store")
    if request.method == 'POST':
        user = flask.g.user
        user_data = flask.g.user_data
        request_data = request.get_json


        # This should be interpreted from jwt later 
        # id = request_data.get('id')
        id = user['uid']
        title = request_data.get('title')
        description = request_data.get('description', None)
        latitude = request_data.get('latitude')
        longitude = request_data.get('longitude')
        instagram = request_data.get('instagram', None)
        tiktok = request_data.get('tiktok', None)
        pinterest = request_data.get('pinterest', None)
        facebook = request_data.get('facebook', None)
        delivery_methods = request_data.get('delivery_methods', [])
        delivery_radius = request_data.get('radius', None)

        for i in range(len(delivery_methods)):
            if delivery_methods[i] == "Local Pickup":
                delivery_methods[i] = 1
            elif delivery_methods[i] == 'Delivery':
                delivery_methods[i] = 2
            else:
                delivery_methods[i] = 3

        if not (id and title and latitude and longitude):
            return {'error': 'Required fields: id, title, latitude, and longitude'}, 400

        insert_seller_query = text(
            'INSERT INTO sellers (id, title, description, instagram, tiktok, pinterest, facebook, latitude, longitude, delivery_radius)'
            'VALUES (;id, :title, :description, :instagram, :tiktok, :pinterest, :facebook, :latitude, :longitude, :delivery_radius)'
        )
        seller_values = {
            "id" : id,
            "title" : title,
            "description" : description, 
            "instagram" : instagram,
            "tiktok" : tiktok, 
            "pinterest" : pinterest,
            "facebook" : facebook,
            "latitude" : latitude,
            "longitude" : longitude,
            "delivery_radius" : delivery_radius
        }

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
