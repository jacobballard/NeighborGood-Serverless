from flask import Request, jsonify, Response
import requests
import functions_framework
import stripe
import os
import json
from shared.firestore_db import db as firestore_db
from shared.auth import is_authenticated_wrapper, headers

stripe.api_key = os.getenv("STRIPE_API_KEY")

@functions_framework.http
def stripe_webhook_payment_intent_succeeded(request: Request):
    # payload = request.get_json()
    print(request)
    try:
        event = stripe.Event.construct_from(
            json.loads(request.get_data()), stripe.api_key
        )
    except ValueError as e:
        return jsonify({'error' : 'lol idek'}), 400
    
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        print(payment_intent)
        print(event.data.object)
        
        cart_id = payment_intent['transfer_group']
        # latest_charge = payment_intent['latest_charge']
        print(cart_id)
        print('cart_id')
        cart_ref = firestore_db.collection('carts').document(cart_id)
        print(stripe.Customer.retrieve(payment_intent['customer']))

        cart_ref.update({'completed' : True, 'charge_id' : payment_intent['latest_charge']})
        
        print('PaymentIntent was successful!')
    else:
        print('unhandled webhook forwarded {}'.format(event.type))
    
    return Response(status=200)