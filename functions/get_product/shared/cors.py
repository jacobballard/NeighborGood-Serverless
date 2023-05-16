from functools import wraps
from flask import make_response

def add_cors_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        h = resp.headers
        h['Access-Control-Allow-Origin'] = '*'
        h['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        h['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        return resp
    return decorated_function

@add_cors_headers
@functions_framework.http
def get_product(request: flask.Request):
    if request.method == 'OPTIONS':
        return '', 204
    # Your function's code here...
