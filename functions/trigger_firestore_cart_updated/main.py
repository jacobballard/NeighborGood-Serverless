import json
import os
from jsondiff import diff
from flask import jsonify
from shared.firestore_db import db as firestore_db
import stripe
from firebase_admin import firestore

stripe.api_key = os.environ['STRIPE_API_KEY']

def trigger_firestore_cart_updated(data, context):
    """Triggered by a change to a Firestore document.
    Args:
        data (dict): The event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    trigger_resource = context.resource

    # print("Function triggered by change to: %s" % trigger_resource)

    # print("\nOld value:")
    # print(json.dumps(data["oldValue"]))

    # print("\nNew value:")
    # print(json.dumps(data["value"]))
    d = diff(data["oldValue"]['fields'], data["value"]['fields'])
    difference = {}

    name = data['value']['name'].split('/')[-1]

    # print(name)
    # print('name')
    cart_dict = firestore_db.collection('carts').document(name).get().to_dict()
    # print(ref.to_dict())
    
    for key, value in d.items():
        # Convert Symbol keys to strings
        if isinstance(key, type(...)):
            key = str(key)
        difference[key] = value

    # print(d)
    # print(difference)
    if 'completed' in difference:
        # print('completed in')

        # Check if the 'completed' field is True
        if difference['completed']['booleanValue'] is True:
            for seller_name, value in cart_dict['transfers'].items():
                # print(seller_name)
                # print(value)
                amount = int(value['price']) + int(value['shipping_fee']) + int(value['taxes'])
                transfer = stripe.Transfer.create(
                    amount=amount,
                    currency='usd',
                    destination=value['stripe_connect_account_id'],
                    transfer_group=name,
                    source_transaction=cart_dict['charge_id'],
                )
                
                seller_ref = firestore_db.collection('stores').document(seller_name).collection('purchases')
                seller_ref.add({
                    'cart_id' : name,
                    'customer_id': cart_dict['customer_id'],
                    'price' : value['price'],#test
                    'products' : value['products'],
                    'taxes' : value['taxes'],
                    'shipping_fee': value['shipping_fee'],
                    'items' : value['items'],
                    'address' : value['shipping_address'] if ('Shipping' in value['dms'] or 'Delivery' in value['dms']) else None,
                    'created_at': firestore.SERVER_TIMESTAMP,
                })

                # print(seller_ref.get())

    
    
    # return ({}, 200)
