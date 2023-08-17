import flask
import requests
import functions_framework
import os
import stripe
from shared.auth import is_authenticated_wrapper, headers

stripe.api_key = os.getenv("STRIPE_API_KEY")

@is_authenticated_wrapper(True)
@functions_framework.http
def finalize_payment(request: flask.Request):
    request_data = request.get_json()
    
