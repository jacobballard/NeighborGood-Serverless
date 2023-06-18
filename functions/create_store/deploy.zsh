#!/bin/zsh
RUN_LOCALLY=false

# Loop through arguments
for arg in "$@"
do
    case $arg in
        --run_locally)
        RUN_LOCALLY=true
        shift # Remove --run_locally from processing
        ;;
        *)
        shift # Remove generic argument from processing
        ;;
    esac
done
STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)
GEOCODING_KEY=$(<$HOME/Desktop/neighborgood/google_maps_geocoding.txt)

source $HOME/Desktop/neighborgood/sql_db_config.txt

if $RUN_LOCALLY; then
  # Command to run locally using functions-framework
  # Copy contents from shared_local to shared
  export STRIPE_API_KEY=$STRIPE_KEY
  export GEOCODING_KEY=$GEOCODING_KEY
  pip install -r requirements.txt
  cp -r ./../shared_local/* ./shared
  functions-framework --target create_store --debug --port 8085
else
  cp -r ./../shared ./

  gcloud functions deploy create_store \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars STRIPE_API_KEY=$STRIPE_KEY,GEOCODING_KEY=$GEOCODING_KEY,DB_USER=$DB_USER,DB_PASS=$DB_PASS,DB_NAME=$DB_NAME,INSTANCE_UNIX_SOCKET=$INSTANCE_UNIX_SOCKET
fi