import functions_framework
from sqlalchemy import create_engine, text
import flask
from database import db

@functions_framework.http
def get_sellers_list(request: flask.Request):
    if request.method == 'POST':
        request_data = request.get_json()
        delivery_method = request_data.get('delivery_method')

        if not delivery_method:
            return {'error': 'Required field: delivery_method'}, 400

        connection = db.connect()
        try:
            query = text(
                'SELECT sellers.id, sellers.name'
                'FROM sellers'
                'JOIN products ON sellers.id = products.seller_id'
                'JOIN product_delivery_methods ON products.id = product_delivery_methods.product_id'
                'WHERE product_delivery_methods.delivery_method_id = :delivery_method'
            )
            result = connection.execute(query, {'delivery_method': delivery_method})
            sellers = [dict(row) for row in result]
            return {'sellers': sellers}, 200
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            connection.close()

    else:
        return {'error': 'Invalid request method'}, 405
