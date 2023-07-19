from sqlalchemy import create_engine
import flask
from flask import jsonify
import functions_framework
import os
from sqlalchemy import text
from shared.sql_db import db as database
from shared.auth import is_authenticated_wrapper, headers

# @is_authenticated_wrapper(True)
# @functions_framework.http
# def get_products(request: flask.Request):
#     request_data = request.get_json()
#     lat = request_data.get('lat')
#     lng = request_data.get('lng')
#     radius = request_data.get('radius', 10)
#     filter_shipping = request_data.get('filter_shipping', False)
#     filter_delivery = request_data.get('filter_delivery', False)
#     filter_pickup = request_data.get('filter_pickup', False)

#     connection = database.connect()

#     # Get products based on filters
#     query = text((
#         "SELECT products.*, sellers.latitude, sellers.longitude "
#         "FROM products "
#         "JOIN sellers ON products.seller_id = sellers.id "
#         "JOIN product_delivery_method ON products.id = product_delivery_method.product_id "
#         "JOIN delivery_method ON product_delivery_method.delivery_method_id = delivery_method.id "
#         "WHERE "
#         "((:filter_shipping AND delivery_method.id = 2)"
#     "OR (:filter_delivery AND delivery_method.id = 3 AND haversine(:lat, :lng, sellers.latitude, sellers.longitude) <= product_delivery_method.delivery_range)"
#     "OR (:filter_pickup AND delivery_method.id = 1 AND haversine(:lat, :lng, sellers.latitude, sellers.longitude) <= :radius)) "
#     "GROUP BY products.id, sellers.latitude, sellers.longitude;"
    
#     ))

#     # products_data = connection.execute(query, {
#     #     'lat': lat,
#     #     'lng': lng,
#     #     'radius': radius,
#     #     'filter_shipping': filter_shipping,
#     #     'filter_delivery': filter_delivery,
#     #     'filter_pickup': filter_pickup
#     # }).fetchall()
#     # print(products_data)
#     # products = [dict(row.items()) for row in products_data]
#     result_proxy = connection.execute(query, {
#     'lat': lat,
#     'lng': lng,
#     'radius': radius,
#     'filter_shipping': filter_shipping,
#     'filter_delivery': filter_delivery,
#     'filter_pickup': filter_pickup
# })

#     column_names = result_proxy.keys()
#     products_data = result_proxy.fetchall()
#     print(products_data)
#     products = [dict(zip(column_names, row)) for row in products_data]
#     print(products)

#     connection.close()

#     return (jsonify({'products': products}), 200, headers)
@is_authenticated_wrapper(True)
@functions_framework.http
def get_products(request: flask.Request):
    request_data = request.get_json()
    lat = request_data.get('lat')
    lng = request_data.get('lng')
    radius = request_data.get('radius', 10)
    filter_shipping = request_data.get('filter_shipping', False)
    filter_delivery = request_data.get('filter_delivery', False)
    filter_pickup = request_data.get('filter_pickup', False)

    connection = database.connect()

    if lat is None or lng is None:
        query = text((
            "SELECT products.*, sellers.latitude, sellers.longitude "
            "FROM products "
            "JOIN sellers ON products.seller_id = sellers.id "
            "JOIN product_delivery_method ON products.id = product_delivery_method.product_id "
            "JOIN delivery_method ON product_delivery_method.delivery_method_id = delivery_method.id "
            "WHERE (:filter_shipping AND delivery_method.id = 2) "
            "ORDER BY products.created_at DESC, products.title ASC;"
        ))
        result_proxy = connection.execute(query, {
            'filter_shipping': filter_shipping
        })
    else:
        query = text((
            "SELECT products.*, sellers.latitude, sellers.longitude "
            "FROM products "
            "JOIN sellers ON products.seller_id = sellers.id "
            "JOIN product_delivery_method ON products.id = product_delivery_method.product_id "
            "JOIN delivery_method ON product_delivery_method.delivery_method_id = delivery_method.id "
            "WHERE "
            "((:filter_shipping AND delivery_method.id = 2)"
            "OR (:filter_delivery AND delivery_method.id = 3 AND haversine(:lat, :lng, sellers.latitude, sellers.longitude) <= product_delivery_method.delivery_range)"
            "OR (:filter_pickup AND delivery_method.id = 1 AND haversine(:lat, :lng, sellers.latitude, sellers.longitude) <= :radius)) "
            "GROUP BY products.id, sellers.latitude, sellers.longitude;"
        ))
        result_proxy = connection.execute(query, {
            'lat': lat,
            'lng': lng,
            'radius': radius,
            'filter_shipping': filter_shipping,
            'filter_delivery': filter_delivery,
            'filter_pickup': filter_pickup
        })

    column_names = result_proxy.keys()
    products_data = result_proxy.fetchall()
    print(products_data)
    products = [dict(zip(column_names, row)) for row in products_data]
    print(products)

    connection.close()

    return (jsonify({'products': products}), 200, headers)
