from sqlalchemy import create_engine, text
import flask
import requests
import functions_framework
import os
import stripe
from shared.firestore_db import db as firestore_db
from shared.sql_db import db as sql_db
from shared.auth import is_authenticated_wrapper, has_required_role, headers

stripe.api_key = os.getenv("STRIPE_API_KEY")
geocoding_key = os.getenv("GEOCODING_KEY")

taxcloud_login_id = os.environ['TAXCLOUD_LOGIN_ID']
taxcloud_api_key = os.environ['TAXCLOUD_API_KEY']
# def check(tc, data, order):
#         del(tc['ErrNumber'])
#         del(tc['ErrDescription'])
#         if tc['Address2'] is None:
#             tc['Address2'] = ''
#         if data['Address1'] == tc['Address1'] and data['Address2'] == tc['Address2'] and data['City'] == tc['City'] and data['State'] == tc['State'] and data['Zip5'] == tc['Zip5'] and data['Zip4'] == tc['Zip4']:
#             print('yay')
#             return None
#         else:
#             print('return suggested addresss')
#             print(tc)
#             print(taxcloud_api_key)
#             return  tc
@is_authenticated_wrapper(False)
@has_required_role("buyer")
@functions_framework.http
def create_store(request: flask.Request):
    print('requested')
    if request.method == 'POST':
        print('top')
        print(request.headers)
        print(request.remote_addr)

        ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        print("iniside")
        user = flask.g.user
        print("User")
        print(user)
        # user_data = flask.g.user_data
        request_data = request.get_json()
        print(request_data)
        seller_business_type = request_data.get('type')
        tax_rate = request_data.get('tax_rate')
    #      if (isBusiness) 'company_name': companyName,
    #   if (isBusiness) 'company_tax_id': companyTaxId,
    #   if (!isBusiness) 'first_name': firstName,
    #   if (!isBusiness) 'last_name': lastName,
    #   if (!isBusiness) 'birth_day': birthDay,
    #   if (!isBusiness) 'birth_month': birthMonth,
    #   if (!isBusiness) 'birth_year': birthYear,
    #   if (!isBusiness) 'ssn_last_four': ssnLastFour,
    # 'bank_account_number': bankAccountNumber,
    #   'bank_routing_number': bankRoutingNumber,
    #   'terms_accepted': termsAccepted,

        bank_account_number = request_data.get('bank_account_number')
        bank_routing_number = request_data.get('bank_routing_number')
        # terms_accepted = request_data.get('terms_accepted')
        terms_time_accepted = request_data.get('terms_time_accepted')
        if (seller_business_type == 'business'):
            print('business')
            company_name = request_data.get('company_name')
            company_tax_id = request_data.get('company_tax_id')
        elif (seller_business_type == 'individual'):
            print('indy')
            first_name = request_data.get('first_name')
            last_name = request_data.get('last_name')
            birth_day = request_data.get('birth_day')
            birth_month = request_data.get('birth_month')
            birth_year = request_data.get('birth_year')
            ssn_last_four = request_data.get('ssn_last_four')
        else:
            print("Oh no we don't have a business type??")

        
        
        id = user['user_id']
        

        title = request_data.get('title')
        description = request_data.get('description', None)

        address = request_data['address']

        
        
        # url = 'https://api.taxcloud.net/1.0/TaxCloud/VerifyAddress'
        

        # print("address billing")
        # print(address)
        if len(address['zip']) > 5:
            address['zip5'] = address['zip'].split("-")[0]
            address['zip4'] = address['zip'].split("-")[1]
        elif len(address['zip']) == 5:
            address['zip5'] = address['zip']
            address['zip4'] = ''
        else:
            return (headers, flask.jsonify({'error':'should never get this'}), 400)
       
        addr_data = {
            "Address1": address['address_line_1'],
            "Address2": address['address_line_2'],
            "City": address['city'],
            "State": address['state'],
            "Zip5": address['zip5'],
            "Zip4": address['zip4'],
            # "apiKey": taxcloud_api_key,
            # "apiLoginID": taxcloud_login_id
        }

        # response_first = requests.post(url=url, json=addr_data)
        # print(response_first)

        # tc_data_billing = response_first.json()
        # print(tc_data_billing)
        # tc_check1_data = check(tc_data_billing, addr_data, 1)
        # return_resp = {'code' : 'suggested_address'}
        # if tc_check1_data is not None:
        #     return_resp['suggested_address'] = tc_check1_data
        #     print(return_resp)
        #     return flask.jsonify(return_resp), 200, headers
            
        


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

            
            
            if (seller_business_type == 'business'):
                stripe_account = stripe.Account.create(
                    type="custom",
                    country="US",
                    email=user["email"],  # Replace with actual email
                    idempotency_key=id,
                    business_type='comapny',
                    metadata={
                        'seller_id' : id,
                    },
                    capabilities={
                        "transfers": {"requested": True},
                    },
                )
                stripe_account_id = stripe_account["id"]
                stripe_account = stripe.Account.modify(
                    id=stripe_account_id,
                    company={
                        "name" : company_name,
                        "tax_id" : company_tax_id,
                    },
                    )
            elif (seller_business_type == 'individual'):
                stripe_account = stripe.Account.create(
                    type="custom",
                    business_type='individual',
                    
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
                stripe_account_id = stripe_account["id"]
                stripe_account = stripe.Account.modify(
                    id=stripe_account_id,
                    individual={
                        "dob": {
                            "day":int(birth_day),
                            "month":int(birth_month),
                            "year":int(birth_year),
                        },
                        "first_name":first_name,
                        "last_name":last_name,
                        "ssn_last_4" : ssn_last_four,
                    },
                    )
            # https://neighborgood.app/#/store/seller_id
                
            business_url = 'https://neighborgood.app/#/store/{}'.format(id)
            stripe_account = stripe.Account.modify(
                id=stripe_account_id,
                business_profile={
                    "url":business_url,
                },
                tos_acceptance={
                    "date":int(terms_time_accepted),
                    "ip":ip_addr,
                },
            )

            stripe.Account.create_external_account(
                id=stripe_account_id,
                external_account={
                    'object':'bank_account',
                    'country':'US',
                    'currency':'usd',
                    'account_number':bank_account_number,
                    'routing_number':bank_routing_number,
                }
            )
            print("done here")
            print(stripe_account)
           
            stripe_account_id = stripe_account["id"]

            # Retrieve the Stripe account
            account = stripe.Account.retrieve(stripe_account_id)
            

            # Get the fields needed for verification
            fields_needed = account['requirements']['currently_due']

            # Print the fields needed for verification
            print('needed fields!!!JBB!OUBOIBO _______++++++--------_!!!')
            print(fields_needed)


            # storefront_id = str(uuid.uuid4())

            # del(addr_data['apiKey'])
            # del(addr_data['apiLoginID'])
            
            doc_ref = firestore_db.collection(u'stores').document(id)
            doc_ref.set({
                u'tax_rate': tax_rate,
                u'title' : title,
                u'description' : description,
                u'latitude': latitude,
                u'longitude': longitude,
                # u'storefront_id' : storefront_id,
                u'address' : addr_data,
                u'delivery_methods' : delivery_methods,

            }, merge=True)
            
            user_ref = firestore_db.collection('users').document(id)

            user_ref.set({
                "role" : "seller",
                u'stripe_connect_account_id': stripe_account["id"],
                u'stripe_onboarding_requirements' : fields_needed,
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
