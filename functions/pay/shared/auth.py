from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import credentials, exceptions, auth
from shared.get_var import get_variable


if get_variable('LAPTOP', False):
    cred = credentials.Certificate('/Users/jacobballard/Library/Mobile Documents/com~apple~CloudDocs/Desktop/neighborgood/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')
else:
    cred= credentials.Certificate('/Users/jacobballard/Desktop/neighborgood/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')



headers = {
    'Access-Control-Allow-Origin': '*',  # Or the specific origin you want to allow
    'Access-Control-Allow-Methods': 'POST,GET',  # Or the methods you want to allow
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',  # Or the headers you want to allow
}

try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(credential=cred)

def is_authenticated_wrapper(all_anonymous_users=True):
    def decorator(f):
        @wraps(f)
        def wrapper(request):

            if request.method == 'OPTIONS':
            # This is a preflight request. Reply successfully:
                
                return ('', 204, headers)
            
            token = request.headers.get('authorization')
            test = request.headers
            

            print(test)
            if not token:
                print("oh no")
                return jsonify({'error': 'No token provided'}), 401

            print(token[7:])
            print("token wrapper worked")
            try:
                user = auth.verify_id_token(token[7:])
                print(user)
                print("booya")
                # print(user.email)
                if not all_anonymous_users and user.get('provider_id') == 'anonymous':
                    return jsonify({'error': 'Anonymous user'}), 401

                g.user = user
            except Exception as e:
                print(f"Exception: {e}")
                return jsonify({'error': 'Invalid token'}), 401

            return f(request)
        return wrapper
    return decorator


def has_required_role(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(request):
            print("inside")
            if not g.user:
                return jsonify({'error': 'User information not found'}), 401

            from .firestore_db import db
            user_ref = db.collection('users').document(g.user['uid'])
            g.user_data = user_ref.get().to_dict()

            if not g.user_data or g.user_data.get('role') != required_role:
                return jsonify({'error': 'Unauthorized'}), 403

            return f(request)
        return wrapper
    return decorator
