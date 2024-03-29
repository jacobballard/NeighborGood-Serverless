import os
import uuid
import stripe
from shared.firestore_db import db as firestore_db
import functions_framework
import flask
from flask import jsonify, request
import requests
import json
from collections import defaultdict
import pprint
from shared.auth import is_authenticated_wrapper, headers

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))
stripe.api_key = os.environ['STRIPE_API_KEY']

taxcloud_login_id = os.environ['TAXCLOUD_LOGIN_ID']
taxcloud_api_key = os.environ['TAXCLOUD_API_KEY']
def check(tc, data, order):
        del(tc['ErrNumber'])
        del(tc['ErrDescription'])
        if tc['Address2'] is None:
            tc['Address2'] = ''
        if data['Address1'] == tc['Address1'] and data['Address2'] == tc['Address2'] and data['City'] == tc['City'] and data['State'] == tc['State'] and data['Zip5'] == tc['Zip5'] and data['Zip4'] == tc['Zip4']:
            print('yay')
            return None
        else:
            print('return suggested addresss')
            return  tc

def sum_modifier(modifiers, modifiers_selections, sellers, seller_key, quantity, index, seller_tax_rate):
    print('sum')
    print(modifiers)
    pprint.pprint(modifiers_selections)
    print(sellers)
    for modifier in modifiers:
        mod_id = modifier['id']
        mod_type = modifier['type']
        mod_required = modifier['required']  
        flag = False
        for modifier_selection in modifiers_selections:
            select_type = modifier_selection['type']
            is_multi_choice = modifier_selection['type'] == 'multi_choice'
            select_id = modifier_selection['id']
            answer = modifier_selection['answer']
            if mod_id == select_id:
                if mod_type == select_type:
                    if is_multi_choice:
                        input_id = modifier_selection['input']
                        choices = modifier['choices']
                        for choice in choices:
                            if choice['id'] == input_id:
                                flag = True
                                if choice['price'] != "":
                                    choice_price = float(choice['price'])
                                    sellers[seller_key]['price'] += choice_price * quantity
                                    sellers[seller_key]['products'][index]['price'] += choice_price * quantity
                                    sellers[seller_key]['taxes'] += (choice_price * quantity) * seller_tax_rate
                    else:
                        flag = True
                        choice_price = float(modifier['price'])
                        
                        if choice_price != "" and answer != "":
                            sellers[seller_key]['price'] += choice_price * quantity
                            print('print')
                            pprint.pprint(sellers)
                            sellers[seller_key]['products'][index]['price'] += choice_price * quantity
                            sellers[seller_key]['taxes'] += choice_price * quantity * seller_tax_rate
        if mod_required and not flag:
            return (jsonify({'code': 'modifier selection required'}), 400, headers)                
@is_authenticated_wrapper(True)
@functions_framework.http
def pay(request):
    data = request.get_json()
    customer_id = flask.g.user['user_id']
    # customer_id = data['customer_id']  # Replace with the customer's Stripe ID
    # product_ids = data['product_ids']  # List of product IDs to purchase
    print(data)
    stripe_customer_id = firestore_db.collection(u'users').document(customer_id).get().get('stripe_customer_id')
    sellers = dict()
    # seller_stripe_ids = dict()

# {'items': 
#  [{'product_id': '64abe744-a3e1-4dc4-b0bd-8cdc3511044f',
#     'seller_id': 'OERQ2hfpAceMnDZOTWJWAWKNTfm2',
#     'quantity': 1,
#     'delivery_method': 'Local pickup', 
#     'modifiers': []}, 
#     {'product_id': '5645c729-d63f-4056-b363-2642cf5d7342', 
#      'seller_id': 'OERQ2hfpAceMnDZOTWJWAWKNTfm2', 
#      'quantity': 1, 
#      'delivery_method': 'Shipping', 
#      'modifiers': [
#          {'id': '0434a0ec-1422-49b9-8db5-804ff64c44d1', 
#           'type': 'text', 
#           'input': 'test'},
#             {'id': '99a4b964-32da-4a8a-a7a1-ce69197733a7',
#             'type': 'multi_choice',
#             'input': '7a47eda8-4f1f-47bc-bbec-a57be7da8b75'}]
#             }]}
#41030 - baked goods



    for item in data['items']:
        seller_key = item['seller_id']
        product_key = item['product_id']
        quantity = int(item['quantity'])
        modifiers_selections = item['modifiers']
        dm = item['delivery_method']
        delivery_method_price = 0.0
        delivery_methods = firestore_db.collection(u'stores').document(seller_key).collection(u'products').document(product_key).get().get('delivery_methods')
        # is_shipping = False
        found_dm = False
        for method in delivery_methods:
            if dm == method['type']:
                found_dm = True
                if dm == 'Shipping':

                    delivery_method_price = float(method['fee']) if method['fee'] != '' else 0
                elif dm == 'Delivery':
                    delivery_method_price = float(method['fee']) if method['fee'] != '' else 0
        
        if not found_dm:
            return jsonify({'error' : 'no such shipping method exists'}), 400, headers
                
        
            
        product = firestore_db.collection(u'stores').document(seller_key).collection(u'products').document(product_key).get()

        modifiers = firestore_db.collection(u'stores').document(seller_key).collection(u'products').document(product_key).get().get('modifiers')
        print(seller_key)
        print(firestore_db.collection(u'stores').document(seller_key).get())
        seller_tax_rate = float(firestore_db.collection(u'stores').document(seller_key).get().get('tax_rate'))
        print(seller_tax_rate)
        print(sellers)
        # print(seller_stripe_ids)
        # print('stripe id')
        index = None
        if seller_key in sellers:
            print(str(product.get('price')))
            print(seller_key)
            print(product_key)
            price = quantity * float(product.get('price'))
            sellers[seller_key]['items'].append(item)
            sellers[seller_key]['price'] += price
            sellers[seller_key]['shipping_fee'] += (delivery_method_price * quantity) if dm == 'Shipping' else delivery_method_price
            # sellers[seller_key]['price'] += (delivery_method_price * quantity) if dm == 'Shipping' else delivery_method_price
            sellers[seller_key]['dms'].add(dm)
            sellers[seller_key]['taxes'] += price * float(seller_tax_rate)
            index = len(sellers[seller_key]['products'])

            sellers[seller_key]['products'].append(dict({
                "Index" : index,
                "ItemID" : product_key,
                # "TIC" : 41030,
                "price": float(product.get('price'))/quantity,
                "Qty": quantity
            }))
        else:
            index = 0
            price = quantity * (float(firestore_db.collection(u'stores').document(seller_key).collection(u'products').document(product_key).get().get('price')))# + delivery_method_price if not is_shipping else 0.0)
            sellers[seller_key] = dict({
                'items' : [item],
                'price' :price, 
                'shipping_fee' : (delivery_method_price * quantity) if dm == 'Shipping' else delivery_method_price,
                'dms':set(dm), 
                'taxes' : price * float(seller_tax_rate),
                'stripe_connect_account_id' : firestore_db.collection(u'users').document(seller_key).get().get('stripe_connect_account_id'),
                'products': [dict({
                "Index" : index,
                "ItemID" : product_key,
                # "TIC" : 41030,
                "price": price,
                "Qty": quantity
                })]
            })
        # sellers[seller_key] += delivery_method_price
        sum_modifier(modifiers=modifiers, modifiers_selections=modifiers_selections, sellers=sellers, seller_key=seller_key, quantity=quantity, index=index,seller_tax_rate=seller_tax_rate)
    # print(sellers)
    # subtotal = sum(sellers.values())
    # platform_fee_percent = 0.05
    
        
        


    
    # for seller in sellers:
    #     sellers[seller] *= 0.98
    
    # platform_fee = subtotal - sum(sellers.values()) + (subtotal * platform_fee_percent)


    # total = (subtotal * 1.06) + platform_fee

    # tax_rate = 0.06 POST https://api.taxcloud.net/1.0/TaxCloud/VerifyAddress
#     # Writable:
# {
#     "Address1": "string",
#     "Address2": "string",
#     "City": "string",
#     "State": "string",
#     "Zip4": "number",
#     "Zip5": "number",
#     "apiKey": "string",
#     "apiLoginID": "string"
# }
    
    # verify_url = 'https://api.taxcloud.net/1.0/TaxCloud/VerifyAddress'
    # address_billing = data['address_billing']

    # print("address billing")
    # print(address_billing)
    # if len(address_billing['zip']) > 5:
    #     address_billing['zip5'] = address_billing['zip'].split("-")[0]
    #     address_billing['zip4'] = address_billing['zip'].split("-")[1]
    # elif len(address_billing['zip']) == 5:
    #     address_billing['zip5'] = address_billing['zip']
    #     address_billing['zip4'] = ''
    # else:
    #     return (headers, jsonify({'error':'should never get this'}), 400)
    address_shipping = data['address_shipping']
    # print("address shipping")
    # print(address_shipping)
    # if len(address_shipping['zip']) > 5:
    #     address_shipping['zip5'] = address_shipping['zip'].split("-")[0]
    #     address_shipping['zip4'] = address_shipping['zip'].split("-")[1]
    # elif len(address_shipping['zip']) == 5:
    #     address_shipping['zip5'] = address_shipping['zip']
    #     address_shipping['zip4'] = ''
    # else:
    #     return (headers, jsonify({'error':'should never get this'}), 400)
    # data_billing = {
    #     "Address1": address_billing['address_line_1'],
    #     "Address2": address_billing['address_line_2'],
    #     "City": address_billing['city'],
    #     "State": address_billing['state'],
    #     "Zip5": address_billing['zip5'],
    #     "Zip4": address_billing['zip4'],
    #     "apiKey": taxcloud_api_key,
    #     "apiLoginID": taxcloud_login_id
    # }

    # data_shipping = {
    #     "Address1": address_shipping['address_line_1'],
    #     "Address2": address_shipping['address_line_2'],
    #     "City": address_shipping['city'],
    #     "State": address_shipping['state'],
    #     "Zip5": address_shipping['zip5'],
    #     "Zip4": address_shipping['zip4'],
    #     "apiKey": taxcloud_api_key,
    #     "apiLoginID": taxcloud_login_id
    # }

    
    # response_first = requests.post(url=verify_url, json=data_billing)

    # response_second = ""
    # tc_check2_data = None
    # print("sbaoibdasbdas data billing")
    # print(data_billing)
    # print(data_shipping)
    # if data_billing != data_shipping:
    #     print('oh no')
    #     response_second = requests.post(url=verify_url, json=data_shipping)
    #     tc_data_shipping = response_second.json()
    #     tc_check2_data = check(tc_data_shipping, data_shipping, 2)
    # print("response")
    # tc_data_billing = response_first.json()
    
    # tc_check1_data = check(tc_data_billing, data_billing, 1)
    # return_resp = {'code' : 'suggested_address'}
    # if tc_check1_data is not None:
    #     return_resp['billing'] = tc_check1_data
    #     if tc_check2_data is not None:
    #         print("bof")
            
            
    #         return_resp['shipping'] = tc_check2_data
    #         print(return_resp)
    #         return jsonify(return_resp), 200, headers
    #     else:
    #         print(return_resp)
    #         return jsonify(return_resp), 200, headers
    # else:
    #     if tc_check2_data is not None:
    #         print("tccheck2data not none")
    #         print(tc_check2_data)
    #         # TODO: Make this shipping?
    #         return_resp['2'] = tc_check2_data
    #         print(return_resp)
    #         return jsonify(return_resp), 200, headers
    #     else:
    #         print("else")
    




    # #https://api.taxcloud.net/1.0/TaxCloud/Lookup

    cart_id = str(uuid.uuid4())
    # # seller_taxes = dict()
    # lookup_url = 'https://api.taxcloud.net/1.0/TaxCloud/Lookup'
    # print('sellers')
    # print(sellers)
    total_shipping_fee = 0.0
    # #seller_str = json.dumps(sellers, indent=4)
    # # print(seller_str)
    for seller_key in sellers.keys():
        print('seller key')
        print(seller_key)
        seller_address = firestore_db.collection(u'stores').document(seller_key).get().get('address')
        sellers[seller_key]['address'] = seller_address
    #     request_body = dict({
    #         "apiKey": taxcloud_api_key,
    #         "apiLoginID": taxcloud_login_id,
    #         "cartID" : cart_id,
    #         "customerID" : customer_id,
    #         "cartItems" : sellers[seller_key]['products']
    #     })
        shipping_fee = 0
        if 'Shipping' in sellers[seller_key]['dms']:
            shipping_fee += float(sellers[seller_key]['shipping_fee'])
            total_shipping_fee += shipping_fee
    #         request_body['cartItems'].append(dict({
    #             "Index": len(request_body['cartItems']),
    #             "ItemID" : "shipping",
    #             "TIC": 10010,
    #             "Price":sellers[seller_key]['shipping_fee'],
    #             "Qty": 1
    #             }))
            
    #     if 'Delivery' in sellers[seller_key]['dms']:
    #         request_body['deliveredBySeller'] = True
    #         shipping_fee += float(sellers[seller_key]['shipping_fee'])
    #     else:
    #         request_body['deliveredBySeller'] = False
    #     print("seller address")
    #     print(seller_address)
    #     print(address_shipping)
    #     origin = {
    #         "Address1" : seller_address['Address1'],
    #         'Address2' : seller_address['Address2'],
    #         "City" : seller_address['City'],
    #         "State" : seller_address['State'],
    #         "Zip4" : seller_address['Zip4'],
    #         "Zip5" : seller_address['Zip5']
    #     }
    #     request_body['origin'] = origin
    #     destination = {
    #         "Address1": address_shipping['address_line_1'],
    #         "Address2": address_shipping['address_line_2'],
    #         "City": address_shipping['city'],
    #         "State": address_shipping['state'],
    #         "Zip5": address_shipping['zip5'],
    #         "Zip4": address_shipping['zip4'],
    #     }
        
    #     request_body['destination'] = destination
    #     # print(request_body)
    #     json_str = json.dumps(request_body, indent=4)
    #     print(json_str)
    #     print('request body')
    #     verify_response = requests.post(url=lookup_url,json=request_body).json()
    #     print(verify_response)
    #     print("verify")
        
    #     if verify_response['ResponseType'] == 3:
    #         # response = verify_response['L
    #         for item in verify_response['CartItemsResponse']:
    #             sellers[seller_key]['taxes'] += float(item['TaxAmount'])
    
    subtotal = 0.0
    taxes = 0.0
    for sell in sellers.keys():
        subtotal += sellers[sell]['price']
        taxes += sellers[sell]['taxes']
    
    platform_fee = (.04 * subtotal)

    # seller_subtotal = subtotal * 0.98

    total_charge = subtotal + platform_fee + taxes
    # platform_fee_displayed = 0.04 * subtotal
    total_charge *= 100
    total_post_stripe_fee = total_charge - ((total_charge * 0.029) + 0.30)
    remainder = total_post_stripe_fee

    print('customer id')
    print(customer_id)
        # Create the payment intent
    payment_intent = stripe.PaymentIntent.create(
        amount=int(total_charge),
        currency='usd',
        customer=stripe_customer_id,
        payment_method_types=['card'],
        transfer_group=cart_id
    )

    print(payment_intent)
    print('intent')

    # # Create separate transfers for each seller
    for seller_account_id in sellers.keys():
        amount = sellers[seller_account_id]['price'] * 98
        remainder -= amount

    cart_ref = firestore_db.collection('carts').document(cart_id)
    print('cart ref')
    print(sellers)
    print(subtotal)
    print(taxes)
    print(total_shipping_fee)
    print(platform_fee)
    print(address_shipping)

    cart_ref.set({
        'customer_id': customer_id,
        'transfers' : sellers,
        'total_charge' : (total_charge / 100),
        'subtotal' : subtotal,
        'taxes' : taxes,
        'shipping' : total_shipping_fee,
        'platform_fee' : platform_fee,
        
        'destination' : address_shipping,
        'completed' : False,
        'items' : data['items'],
        'payment_id' : payment_intent['id'],
        
    })
    print(total_charge)
    print('total')
        
    return (jsonify({'client_secret' : payment_intent.client_secret, 
                     'total_charge' : (total_charge / 100),
                     'subtotal' : subtotal,
                     'taxes' : taxes,
                     'shipping' : total_shipping_fee,
                     'platform_fee' : platform_fee,
                     }), 200, headers)
    # # Create separate transfers for each seller
    # for seller_account_id in sellers.keys():
    #     amount = sellers[seller_account_id]['price'] * 98
    #     remainder -= amount
    #     transfer = stripe.Transfer.create(
    #         amount=int(amount),
    #         currency='usd',
    #         destination=sellers[seller_account_id]['stripe_connect_account_id'],
    #         transfer_group=cart_id
    #     )
        
