import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, exceptions
from shared.get_var import get_variable


if get_variable('LAPTOP', False):
    print('true')
    cred = credentials.Certificate('/Users/jacobballard/Library/Mobile Documents/com~apple~CloudDocs/Desktop/neighborgood/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')
else:
    print('false')
    cred= credentials.Certificate('/Users/jacobballard/Desktop/neighborgood/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')

# # from firebase_admin import exceptions
# cred= credentials.Certificate('/Users/jacobballard/Desktop/neighborgood/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')
# cred = credentials.Certificate('/Users/jacobballard/Library/Mobile Documents/com~apple~CloudDocs/Desktop/neighborgood/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')
# PROJECT_ID = "pastry-6b817"

try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(credential=cred)

db = firestore.client()
