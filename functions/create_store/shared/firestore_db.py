import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
PROJECT_ID = "pastry-6b817"

default_app = firebase_admin.initialize_app()
db = firestore.client()