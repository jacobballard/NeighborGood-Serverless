#!/bin/zsh

# Read Stripe secret key from file
STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)
cp -r ./../shared ./
# Deploy the function
gcloud functions deploy on_user_created \
  --runtime python310 \
  --trigger-event providers/firebase.auth/eventTypes/user.create \
  --trigger-resource pastry-6b817 \
  --set-env-vars STRIPE_API_KEY=$STRIPE_KEY

  
