import json
from jsondiff import diff
from flask import jsonify

def trigger_firestore_cart_updated(data, context):
    """Triggered by a change to a Firestore document.
    Args:
        data (dict): The event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    trigger_resource = context.resource

    print("Function triggered by change to: %s" % trigger_resource)

    print("\nOld value:")
    print(json.dumps(data["oldValue"]))

    print("\nNew value:")
    print(json.dumps(data["value"]))
    d = diff(data["oldValue"]['fields'], data["value"]['fields'])
    difference = {}
    
    for key, value in d.items():
        # Convert Symbol keys to strings
        if isinstance(key, type(...)):
            key = str(key)
        difference[key] = value

    print(d)
    print(difference)
    if 'completed' in difference:
        print('completed in')

        # Check if the 'completed' field is True
        if difference['completed']['booleanValue'] is True:
            print('is true')
    
    print(type(d))
    print('\nDiff: ')
    print(d)
    
    print(context)
    print(data)
    # return ({}, 200)
