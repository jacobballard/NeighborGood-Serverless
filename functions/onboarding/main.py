import stripe
# from ...shared import database
# from ...shared.sql_db import db
# from ...shared.auth import is_authenticated_wrapper, has_required_role
from shared.sql_db import db
from shared.auth import is_authenticated_wrapper, has_required_role

def create_stripe_account(user_data):
    try:
        if user_data['business_type'] == 'individual':
            account = stripe.Account.create(
                type='custom',
                country=user_data['country'],
                email=user_data['email'],
                business_type='individual',
                individual={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'dob': {
                        'day': user_data['dob_day'],
                        'month': user_data['dob_month'],
                        'year': user_data['dob_year'],
                    },
                    'address': user_data['address'],
                    'phone': user_data['phone'],
                    'email': user_data['email'],
                },
                requested_capabilities=['transfers'],
            )
        elif user_data['business_type'] == 'company':
            account = stripe.Account.create(
                type='custom',
                country=user_data['country'],
                email=user_data['email'],
                business_type='company',
                company={
                    'name': user_data['business_name'],
                    'tax_id': user_data['business_tax_id'],
                },
                requested_capabilities=['transfers'],
            )
        else:
            return {'error': 'Invalid business type'}, 400

        return account.id
    except InvalidRequestError as e:
        # This will catch any Stripe validation errors and return a meaningful error message
        return {'error': str(e)}, 400