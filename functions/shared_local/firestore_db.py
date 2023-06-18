import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, exceptions

# from firebase_admin import exceptions

cred = credentials.Certificate('/Users/jacobballard/Desktop/neighborgood/pastry-6b817-firebase-adminsdk-agnbu-37de702e34.json')
# PROJECT_ID = "pastry-6b817"

try:
    firebase_admin.get_app()
except:
    firebase_admin.initialize_app(credential=cred)

db = firestore.client()
