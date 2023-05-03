from sqlalchemy import create_engine
import flask
from flask import jsonify
import functions_framework
import os
from sqlalchemy import text

db_user = 'postgres'
db_pass = 'postgres'
db_name = 'postgres'
db_host = 'localhost'
db_port = '5432'

connection_string = f'postgresql://@{db_host}/{db_name}'
db = create_engine(connection_string)

@functions_framework.http
def get_all_products(request : flask.request):
    try:
        request_data = request.args.to_dict()
        

        lat = request_data.get('latitude', None)
        lng = request_data.get('longitude', None)
        radius = request_data.get('radius', None)
        pickup = request_data.get('pickup', None)
        page = request_data.get('page', 1)
        page_size = 10
        print("good")
        print(lat + "lat")
        print(lng)

        select_sellers_lat_lng = ', sellers.lat, sellers.lng' if lat and lng else ''
        join_sellers = 'INNER JOIN sellers ON products.seller_id = sellers.id' if lat and lng or pickup else ''
        pickup_condition = f"AND products.pickup = {pickup}" if pickup is not None else ''
        location_condition = f"AND earth_box(ll_to_earth(sellers.lat, sellers.lng), {radius}) @> ll_to_earth({lat}, {lng})" if lat and lng else ''

        query = (
            "SELECT products.*" + 
            select_sellers_lat_lng + 
            " FROM products " +
            join_sellers +
            " WHERE TRUE " +
            pickup_condition +
            location_condition 
        )

        connection = db.connect()
        result = connection.execute(text(query))
        products = result.fetchall()
        total_products = len(products)
        products = products[(page - 1) * page_size: page * page_size]

        response = {
            'total_products': total_products,
            'products': [dict(zip(row.keys(), row)) for row in products]
        }

        connection.close()
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error" : str(e)}), 500
