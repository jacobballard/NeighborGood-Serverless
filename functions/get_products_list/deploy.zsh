#!/bin/zsh

# Read Stripe secret key from file
source $HOME/Desktop/neighborgood/sql_db_config.txt
cp -r ./../shared ./

gcloud functions deploy get_products_list \
  --runtime python310 \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars DB_USER=$DB_USER,DB_PASS=$DB_PASS,DB_NAME=$DB_NAME,INSTANCE_UNIX_SOCKET=$INSTANCE_UNIX_SOCKET