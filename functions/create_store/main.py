from sqlalchemy import create_engine, text
import flask
import requests
import functions_framework
import os
import stripe
from shared.firestore_db import db as firestore_db
from shared.sql_db import db as sql_db
from shared.auth import is_authenticated_wrapper, has_required_role, headers
from shared.cors import add_cors_headers
from shared.returned import json_abort
stripe.api_key = os.getenv("STRIPE_API_KEY")
geocoding_key = os.getenv("GEOCODING_KEY")


@is_authenticated_wrapper(False)
@has_required_role("buyer")
@functions_framework.http
def create_store(request: flask.Request):

    # if request.method == 'OPTIONS':
    # # This is a preflight request. Reply successfully:
    #     headers = {
    #         'Access-Control-Allow-Origin': '*',  # Or the specific origin you want to allow
    #         'Access-Control-Allow-Methods': 'POST',  # Or the methods you want to allow
    #         'Access-Control-Allow-Headers': 'Content-Type,Authorization',  # Or the headers you want to allow
    #     }
    #     return ('', 204, headers)


    print("then create storea")
    if request.method == 'POST':
        print("iniside")
        user = flask.g.user
        print("User")
        print(user)
        user_data = flask.g.user_data
        request_data = request.get_json()


        # TODO : Call stripe api for connected custom account in us with transfer capability.

        # stripe_account_id = create_stripe_account(user_data)
        # if 'error' in stripe_account_id:
        #     return stripe_account_id
        # This should be interpreted from jwt later 
        # id = request_data.get('id')
        id = user['user_id']

        title = request_data.get('title')
        description = request_data.get('description', None)
        # latitude = request_data.get('latitude')
        # longitude = request_data.get('longitude')

        address = request_data.get('address')
        if address is None:
            return {'error': 'Required fields: address'}, 400

        address_line_1 = address.get('address_line_1') or ''
        address_line_2 = address.get('address_line_2') or ''
        city = address.get('city') or ''
        state = address.get('state') or ''
        zip = address.get('zip') or ''

        address_joined = ', '.join([address_line_1, address_line_2, city, state, zip]).strip()

        # URL encode the address
        address_util = requests.utils.quote(address_joined)
        
        print(geocoding_key)
        print('key')
        response = requests.get(
            url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address_util}&key={geocoding_key}'

        )

        print("Made it past ")
        print(address)
        print(zip)


        geocode_result = response.json()

        print(geocode_result)

        if not geocode_result['results']:
            return {'error': 'invalid-address'}, 400

        latitude = geocode_result['results'][0]["geometry"]["location"]["lat"]
        longitude = geocode_result['results'][0]["geometry"]["location"]["lng"]

        print(latitude)
        print('lat')

        # TODO : DELIVERY METHODS...
        
        # instagram = request_data.get('instagram', None)
        # tiktok = request_data.get('tiktok', None)
        # pinterest = request_data.get('pinterest', None)
        # facebook = request_data.get('facebook', None)
        delivery_methods = request_data.get('delivery_methods')
        print("dm")
        print(delivery_methods)
        # local = delivery_methods.get('local_pickup')
        # delivery = delivery_methods.get('delivery')
        # shipping = delivery_methods.get('shipping')

        

        if not (id and title and latitude and longitude):
            return {'error': 'Required fields: id, title, latitude, and longitude'}, 400

        insert_seller_query = text(
            'INSERT INTO sellers (id, title, latitude, longitude)'
            'VALUES (:id, :title, :latitude, :longitude)'
        )

        seller_values = {
            "id" : id,
            "title" : title,
            # "description" : description, 
            # "instagram" : instagram,
            # "tiktok" : tiktok, 
            # "pinterest" : pinterest,
            # "facebook" : facebook,
            "latitude" : latitude,
            "longitude" : longitude,
            # "delivery_radius" : delivery_radius,
            # "stripe_account_id" : stripe_account_id
        }
        


        connection = sql_db.connect()
        trans = connection.begin()

        try:
            connection.execute(insert_seller_query, seller_values)
            print("success")
            # for method in delivery_methods:
            #     insert_delivery_methods_query = f"""
            #         INSERT INTO seller_delivery_methods (seller_id, delivery_method_id)
            #         VALUES (%s, %s)
            #     """
            #     connection.execute(insert_delivery_methods_query, (id, method))

                # if 'image_urls' in request_data:
                #     image_urls = request_data.get('image_urls')
                #     if isinstance(image_urls, list):
                #         for image_url in image_urls:
                #             insert_image_query = text(
                #                 'INSERT INTO seller_images (seller_id, image_url) VALUES (:seller_id, :image_url)'
                #             )
                #             connection.execute(insert_image_query, {"seller_id" : id, "image_url" : image_url})
            
            # Do the stripe create connect account here.

            #Then add it to firestore
            # trans.commit()
            # connection.close()

            # return {'success': 'Store created successfully'}, 200

        except Exception as e:
            trans.rollback()
            connection.close()
            print(e)
            return {'error': str(e)}, 500
        

        try:

            print(user['email'])

            print('email')
            
            
            stripe_account = stripe.Account.create(
                type="custom",
                country="US",
                email=user["email"],  # Replace with actual email
                idempotency_key=id,
                metadata={
                    'seller_id' : id,
                },
                capabilities={
                    "transfers": {"requested": True},
                },
            )
           
            

            
            
            doc_ref = firestore_db.collection(u'stores').document(id)
            doc_ref.set({
                u'title' : title,
                u'description' : description,
                
                u'address' : address,
                u'delivery_methods' : delivery_methods,

            }, merge=True)

            user_ref = firestore_db.collection('users').document(id)

            user_ref.set({
                "role" : "seller",
                u'stripe_connect_account_id': stripe_account["id"],
            }, merge=True)


        except Exception as e:
            print(e)
            print("stripe failed")
            return {'error': str(e)}, 500
        try:
            print("committing")
            trans.commit()
            connection.close()
            print("done")
        except Exception as e:
            trans.rollback()
            return {'error' : 'Failed to create store: ' + str(e)}
        
        return ('', 204, headers)

    else:
        return ({'error': 'Invalid request method'}, 405, headers)
