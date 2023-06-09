#!/bin/zsh

STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)
GEOCODING_KEY=$(<$HOME/Desktop/neighborgood/google_maps_geocoding.txt)

source $HOME/Desktop/neighborgood/sql_db_config.txt


cp -r ./../shared ./

# gcloud functions deploy create_store \
#   --runtime python310 \
#   --trigger-http \
#   --allow-unauthenticated \
#   --set-env-vars STRIPE_API_KEY=$STRIPE_KEY,GEOCODING_KEY=$GEOCODING_KEY,DB_USER=$DB_USER,DB_PASS=$DB_PASS,DB_NAME=$DB_NAME,INSTANCE_UNIX_SOCKET=$INSTANCE_UNIX_SOCKET