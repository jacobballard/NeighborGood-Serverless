# from functools import wraps
# from flask import request, jsonify, globals
# from firebase_admin import auth
# from functools import wraps

# user = None
# user_data = None

# def is_authenticated_wrapper(all_anonymous_users=True):
#     def decorator(f):
#         @wraps(f)
#         def wrapper(request, *args, **kwargs):
#             token = request.headers.get('Authorization')
#             if not token:
#                 return jsonify({'error': 'No token provided'}), 401

#             try:
#                 user = auth.verify_id_token(token)
#                 if not all_anonymous_users and user.get('sign_in_provider') == 'anonymous':
#                     return jsonify({'error': 'Anonymous user'}), 401

#                 kwargs['user'] = user
#             except Exception as e:
#                 return jsonify({'error': 'Invalid token'}), 401

#             return f(request, *args, **kwargs)
#         return wrapper
#     return decorator


# def has_required_role(required_role):
#     def decorator(f):
#         @wraps(f)
        
#         def wrapper(request, *args, **kwargs):
#             user = kwargs.pop('user', None)
#             if not user:
#                 return jsonify({'error': 'User information not found'}), 401

#             from .firestore_db import db
#             user_ref = db.collection('users').document(user['uid'])
#             user_data = user_ref.get().to_dict()

#             if not user_data or user_data.get('role') != required_role:
#                 return jsonify({'error': 'Unauthorized'}), 403

#             return f(request, *args, **kwargs)
#         return wrapper
#     return decorator
from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

cred = credentials.Certificate('/Users/jacobballard/Desktop/NeighborGood/Serverless/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')
firebase_admin.initialize_app(cred)

def is_authenticated_wrapper(all_anonymous_users=True):
    def decorator(f):
        @wraps(f)
        def wrapper(request):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401

            print(token[7:])
            print("token wrapper worked")
            try:
                user = auth.verify_id_token(token[7:])
                
                print("booya")
                print(user.email)
                if not all_anonymous_users and user.get('sign_in_provider') == 'anonymous':
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
