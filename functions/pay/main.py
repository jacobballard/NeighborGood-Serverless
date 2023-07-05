import os
import stripe
from shared.firestore_db import db
import functions_framework
from flask import jsonify, request
import requests
from collections import defaultdict
from shared.auth import is_authenticated_wrapper, headers

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

def sum_modifier(modifiers, modifiers_selections, sellers, seller_key, quantity):
    print('sum')
    print(modifiers)
    print(modifiers_selections)
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
            if mod_id == select_id:
                if mod_type == select_type:
                    if is_multi_choice:
                        input_id = modifier_selection['input']
                        choices = modifier['choices']
                        for choice in choices:
                            if choice['id'] == input_id:
                                flag = True
                                if choice['price'] != "":
                                    sellers[seller_key] += float(choice['price']) * quantity
                                
                    else:
                        flag = True
                        price = modifier['price']
                        
                        if price != "":
                            sellers[seller_key] += float(price) * quantity
        if mod_required and not flag:
            return (jsonify({'code': 'modifier selection required'}), 400, headers)                
@is_authenticated_wrapper(True)
@functions_framework.http
def pay(request):
    data = request.get_json()

    # customer_id = data['customer_id']  # Replace with the customer's Stripe ID
    # product_ids = data['product_ids']  # List of product IDs to purchase
    print(data)

    sellers = dict()
    seller_stripe_ids = dict()

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
#41030 - baked goodss



    for item in data['items']:
        seller_key = item['seller_id']
        product_key = item['product_id']
        quantity = int(item['quantity'])
        modifiers_selections = item['modifiers']
        dm = item['delivery_method']
        delivery_method_price = 0.0
        delivery_methods = db.collection(u'stores').document(seller_key).collection(u'products').document(product_key).get().get('delivery_methods')

        found_dm = False
        for method in delivery_methods:
            if dm == method['type']:
                found_dm = True
                if dm != 'Local pickup':
                    delivery_method_price = float(method['fee'])
                
                
            
        
        modifiers = db.collection(u'stores').document(seller_key).collection(u'products').document(product_key).get().get('modifiers')
        seller_stripe_ids = db.collection(u'users').document(seller_key).get().get('stripe_connect_account_id')
        print(seller_stripe_ids)
        print('stripe id')
        if seller_key in sellers:
            sellers[seller_key] += quantity * float(db.collection(u'users').document(seller_key).collection(u'products').document(product_key).get().get('price'))
            print(sellers)
            
        else:
            sellers[seller_key] = quantity * float(db.collection(u'users').document(seller_key).collection(u'products').document(product_key).get().get('price'))
        # sellers[seller_key] += 
        sum_modifier(modifiers=modifiers, modifiers_selections=modifiers_selections, sellers=sellers, seller_key=seller_key, quantity=quantity)
    # print(sellers)
    # subtotal = sum(sellers.values())
    # platform_fee_percent = 0.05
    
    # for seller in sellers:
    #     sellers[seller] *= 0.98
    
    platform_fee = subtotal - sum(sellers.values()) + (subtotal * platform_fee_percent)


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
    
    url = 'https://api.taxcloud.net/1.0/TaxCloud/VerifyAddress'
    address_billing = data['address_billing']

    print("address billing")
    print(address_billing)
    if len(address_billing['zip']) > 5:
        address_billing['zip5'] = address_billing['zip'].split("-")[0]
        address_billing['zip4'] = address_billing['zip'].split("-")[1]
    elif len(address_billing['zip']) == 5:
        address_billing['zip5'] = address_billing['zip']
        address_billing['zip4'] = ''
    else:
        return (headers, jsonify({'error':'should never get this'}), 400)
    address_shipping = data['address_shipping']
    print("address shipping")
    print(address_shipping)
    if len(address_shipping['zip']) > 5:
        address_shipping['zip5'] = address_shipping['zip'].split("-")[0]
        address_shipping['zip4'] = address_shipping['zip'].split("-")[1]
    elif len(address_shipping['zip']) == 5:
        address_shipping['zip5'] = address_shipping['zip']
        address_shipping['zip4'] = ''
    else:
        return (headers, jsonify({'error':'should never get this'}), 400)
    data_billing = {
        "Address1": address_billing['address_line_1'],
        "Address2": address_billing['address_line_2'],
        "City": address_billing['city'],
        "State": address_billing['state'],
        "Zip5": address_billing['zip5'],
        "Zip4": address_billing['zip4'],
        "apiKey": taxcloud_api_key,
        "apiLoginID": taxcloud_login_id
    }

    data_shipping = {
        "Address1": address_shipping['address_line_1'],
        "Address2": address_shipping['address_line_2'],
        "City": address_shipping['city'],
        "State": address_shipping['state'],
        "Zip5": address_shipping['zip5'],
        "Zip4": address_shipping['zip4'],
        "apiKey": taxcloud_api_key,
        "apiLoginID": taxcloud_login_id
    }

    
    response_first = requests.post(url=url, json=data_billing)

    response_second = ""
    tc_check2_data = ""
    print("sbaoibdasbdas data billing")
    print(data_billing)
    print(data_shipping)
    if data_billing != data_shipping:
        print('oh no')
        response_second = requests.post(url=url, json=data_shipping)
        tc_data_shipping = response_second.json()
        tc_check2_data = check(tc_data_shipping, data_shipping, 2)
    print("response")
    tc_data_billing = response_first.json()
    
    tc_check1_data = check(tc_data_billing, data_billing, 1)
    return_resp = {'code' : 'suggested_address'}
    if tc_check1_data is not None:
        return_resp['billing'] = tc_check1_data
        if tc_check2_data is not None:
            print("bof")
            
            
            return_resp['shipping'] = tc_check2_data
            print(return_resp)
            return jsonify(return_resp), 200, headers
        else:
            print(return_resp)
            return jsonify(return_resp), 200, headers
    else:
        if tc_check2_data is not None:

            return_resp['2'] = tc_check2_data
            print(return_resp)
            return jsonify(return_resp), 200, headers
    




    #https://api.taxcloud.net/1.0/TaxCloud/Lookup


    
    
    



    #     # Create the payment intent
    # payment_intent = stripe.PaymentIntent.create(
    #     amount=total_amount,
    #     currency='usd',
    #     customer=customer_id,
    #     payment_method_types=['card'],
    # )

    # # Create separate transfers for each seller
    # for seller_account_id, amount in sellers_amount.items():
    #     transfer = stripe.Transfer.create(
    #         amount=amount,
    #         currency='usd',
    #         destination=seller_account_id,
    #     )
        
    # # Transfer the platform fee to your own Stripe Connect account
    # stripe.Transfer.create(
    #     amount=int(platform_fee * 100),  # Stripe expects the amount in cents
    #     currency='usd',
    #     destination=os.environ['YOUR_STRIPE_ACCOUNT_ID'],
    # )



    # Fetch product prices from the SQL products table
    # connection = db.connect()
    # cursor = connection.cursor()
    # cursor.execute("SELECT id, seller_account_id, price FROM products WHERE id IN (%s)" % ','.join(['%s']*len(product_ids)), product_ids)

    # Calculate amount owed to each seller
    # sellers_amount = defaultdict(int)
    # for product_id, seller_account_id, price in cursor.fetchall():
    #     sellers_amount[seller_account_id] += price * 100  # in cents

    # # Calculate fees and total amount
    # total_amount = 0
    # for seller_account_id, amount in sellers_amount.items():
    #     your_fee = int(amount * 0.03)  # 3% of the amount
    #     total_amount += amount + your_fee

    # try:
    #     # Create the payment intent
    #     payment_intent = stripe.PaymentIntent.create(
    #         amount=total_amount,
    #         currency='usd',
    #         customer=customer_id,
    #         payment_method_types=['card'],
    #     )

    #     # Create separate transfers for each seller
    #     for seller_account_id, amount in sellers_amount.items():
    #         your_fee = int(amount * 0.05)
    #         transfer = stripe.Transfer.create(
    #             amount=amount,
    #             currency='usd',
    #             destination=seller_account_id,
    #             source_transaction=payment_intent.charges.data[0].id,
    #             transfer_group=payment_intent.charges.data[0].transfer_group,
    #         )
    #         stripe.Transfer.create(
    #             amount=your_fee,
    #             currency='usd',
    #             destination=os.environ['YOUR_STRIPE_ACCOUNT_ID'],
    #             source_transaction=payment_intent.charges.data[0].id,
    #             transfer_group=payment_intent.charges.data[0].transfer_group,
    #         )

    #     return jsonify(payment_intent)
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 400
    # finally:
    #     connection.close()
