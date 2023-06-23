import os
import stripe
from shared.firestore_db import db
from flask import jsonify, request
from collections import defaultdict


stripe.api_key = os.environ['STRIPE_SECRET_KEY']

def pay(request):
    data = request.get_json()

    # customer_id = data['customer_id']  # Replace with the customer's Stripe ID
    # product_ids = data['product_ids']  # List of product IDs to purchase
    print(data)

    # Fetch product prices from the SQL products table
    # connection = db.connect()
    # cursor = connection.cursor()
    # cursor.execute("SELECT id, seller_account_id, price FROM products WHERE id IN (%s)" % ','.join(['%s']*len(product_ids)), product_ids)

    # Calculate amount owed to each seller
    sellers_amount = defaultdict(int)
    for product_id, seller_account_id, price in cursor.fetchall():
        sellers_amount[seller_account_id] += price * 100  # in cents

    # Calculate fees and total amount
    total_amount = 0
    for seller_account_id, amount in sellers_amount.items():
        your_fee = int(amount * 0.03)  # 3% of the amount
        total_amount += amount + your_fee

    try:
        # Create the payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='usd',
            customer=customer_id,
            payment_method_types=['card'],
        )

        # Create separate transfers for each seller
        for seller_account_id, amount in sellers_amount.items():
            your_fee = int(amount * 0.05)
            transfer = stripe.Transfer.create(
                amount=amount,
                currency='usd',
                destination=seller_account_id,
                source_transaction=payment_intent.charges.data[0].id,
                transfer_group=payment_intent.charges.data[0].transfer_group,
            )
            stripe.Transfer.create(
                amount=your_fee,
                currency='usd',
                destination=os.environ['YOUR_STRIPE_ACCOUNT_ID'],
                source_transaction=payment_intent.charges.data[0].id,
                transfer_group=payment_intent.charges.data[0].transfer_group,
            )

        return jsonify(payment_intent)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        connection.close()
