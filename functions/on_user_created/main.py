import os
from firebase_admin import auth
from firebase_admin.auth import UserRecord
from google.cloud import functions_v1
# from shared.firestore_db import db
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import stripe
from shared.firestore_db import db

stripe.api_key = os.getenv("STRIPE_API_KEY")

def on_user_created(data, context):

    
    # Check if the user is not anonymous
    # if data.providerData[0].providerId == 'password':
    # Add the "buyer" role to the users collection
    user_ref = db.collection('users').document(data["uid"])
    
    print("data")
    print(data)
    # if not data.email:
    #     return
    
    if "email" in data:
        customer = stripe.Customer.create(
        email=data["email"],
        metadata={
            "user_id": data["uid"],
        })
        user_ref.set({
        "role": "buyer",
        "stripe_customer_id": customer["id"],
        })
    else:
        customer = stripe.Customer.create(
        metadata={
            "user_id": data["uid"],
        })
        user_ref.set({
            "role": "guest",
            "stripe_customer_id" : customer["id"],
        })
        

    return 'User role added successfully', 200

# The function should be named in the following format: "functions_AUTH_TRIGGER_NAME"
# functions_AUTH_ON_CREATE = functions_v1.CloudFunction(on_user_created)
