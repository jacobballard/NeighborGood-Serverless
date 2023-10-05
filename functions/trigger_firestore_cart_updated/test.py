from google.cloud import firestore
from uuid import uuid4
client = firestore.Client(project="pastry-6b817")
rand = str(uuid4())
client.collection("carts").document(rand).set({
    'destination' : {
        'Address1' : '2386 Randolph Ct',
        'Address2' : '',
        'City': 'Lexington',
        'State' : 'KY',
        'Zip4' : '2620',
        'Zip5' : '40503'
    },
    'items' : [
        {
            'delivery_method': 'Local pickup',
            'modifiers' : [
                {
                    'id' : '1c45a61b-11b6-40dc-8585-b1543ab8a66c',
                    'input': '88274add-076e-48d0-80bf-ca4e913af256',
                    'type': 'multi_choice'
                }
            ],
            'product_id' : '1487e359-e9c0-43d4-838e-81265605da58',
            'quantity': 1,
            'seller_id': 'TvVFv49AOUSdzbXe9FKa1AUZGLh2',
        }
    ],
    'origin' : {
        'Address1' : '2386 Randolph Ct',
        'Address2': '',
        'City': 'Lexington',
        'State': 'KY',
        'Zip4': '2620',
        'Zip5': '40503'
    },
    'payment_id': 'pi_3NrUsWExW75aEFO91B5nax9Q',
    'remainder': 29.5399999999,
    'taxes': 0,
    'total_charge': 1040,
    'transfers': {
        'TvVFv49AOUSdzbXe9FKa1AUZGLh2' : {
            'dms' : [
                'Local pickup',
            ],
            'price': 10,
            'items' : [
                {
                    'delivery_method': 'Local pickup',
                    'modifiers' : [
                        {
                            'id' : '1c45a61b-11b6-40dc-8585-b1543ab8a66c',
                            'input': '88274add-076e-48d0-80bf-ca4e913af256',
                            'type': 'multi_choice'
                        }
                    ],
                    'product_id' : '1487e359-e9c0-43d4-838e-81265605da58',
                    'quantity': 1,
                    'seller_id': 'TvVFv49AOUSdzbXe9FKa1AUZGLh2',
                }
            ],
            'products':[
                {
                    'Index': 0,
                    'ItemID': '1487e359-e9c0-43d4-838e-81265605da58',
                    'Price': 10,
                    'Qty': 1,
                    'TIC': 41030,
                }
            ],
            'shipping_fee' : 0,
            'stripe_connect_account_id' : 'acct_1NuMbERQYtKQ2EmF',
            'taxes': 0
        }
    }
})

client.collection("carts").document(rand).update({'completed': True})

print(client.collection("carts").document(rand).get().to_dict())
# print(client.collection("carts").document("14a92c56-0124-4101-a3a3-7b037e934312").get().to_dict())