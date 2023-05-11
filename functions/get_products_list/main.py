from sqlalchemy import create_engine
import flask
from flask import jsonify
import functions_framework
import os
from sqlalchemy import text
from shared import database

@functions_framework.http
def get_all_products(request: flask.Request):
    request_data = request.get_json()
    lat = request_data.get('lat')
    lng = request_data.get('lng')
    radius = request_data.get('radius', 10)
    filter_shipping = request_data.get('filter_shipping', False)
    filter_delivery = request_data.get('filter_delivery', False)
    filter_pickup = request_data.get('filter_pickup', False)

    connection = database.db.connect()

    # Get products based on filters
    query = text((
        "SELECT products.*, sellers.lat, sellers.lng, sellers.delivery_radius "
        "FROM products "
        "JOIN sellers ON products.seller_id = sellers.id "
        "JOIN product_delivery_methods ON products.id = product_delivery_methods.product_id "
        "JOIN delivery_methods ON product_delivery_methods.delivery_method_id = delivery_methods.id "
        "WHERE "
        "(:filter_shipping AND delivery_methods.method_name = 'Shipping') "
        "OR (:filter_delivery AND delivery_methods.method_name = 'Delivery' AND haversine(:lat, :lng, sellers.lat, sellers.lng) <= sellers.delivery_radius) "
        "OR (:filter_pickup AND delivery_methods.method_name = 'Pickup' AND haversine(:lat, :lng, sellers.lat, sellers.lng) <= :radius)"
    ))

    products_data = connection.execute(query, {
        'lat': lat,
        'lng': lng,
        'radius': radius,
        'filter_shipping': filter_shipping,
        'filter_delivery': filter_delivery,
        'filter_pickup': filter_pickup
    }).fetchall()

    products = [dict(zip(product.keys(), product)) for product in products_data]

    connection.close()

    return {'products': products}, 200
