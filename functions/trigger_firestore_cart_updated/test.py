from google.cloud import firestore

client = firestore.Client(project="pastry-6b817")
client.collection("carts").document("new").set({'foo': 'bar'})

client.collection("carts").document("new").update({'completed': True})

print(client.collection("carts").document("new").get().to_dict())
print(client.collection("carts").document("14a92c56-0124-4101-a3a3-7b037e934312").get().to_dict())

# After starting emulator you have to enable the firestore trigger
# curl --location --request PUT 'http://localhost:8102/emulator/v1/projects/pastry-6b817/triggers/Test' \
# --header 'Content-Type: application/json' \
# --data-raw '{
#    "eventTrigger": {
#        "resource": "projects/pastry-6b817/databases/(default)/documents/carts/{id}", 
#        "eventType": "providers/cloud.firestore/eventTypes/document.update",
#        "service": "firestore.googleapis.com"
#    }
# }'
