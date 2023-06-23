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
# ## Mac Mini:
# STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)

# # Actual path...
# # /Users/jacobballard/Library/Mobile Documents/com~apple~CloudDocs/Desktop/neighborgood/stripe_key.txt
# GEOCODING_KEY=$(<$HOME/Desktop/neighborgood/google_maps_geocoding.txt)

# source $HOME/Desktop/neighborgood/sql_db_config.txt

STRIPE_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/stripe_key.txt)


if $RUN_LOCALLY; then
  # Command to run locally using functions-framework
  # Copy contents from shared_local to shared
  export STRIPE_API_KEY=$STRIPE_KEY
#   export GEOCODING_KEY=$GEOCODING_KEY
  pip install -r requirements.txt
  cp -r ./../shared_local/* ./shared
  functions-framework --target pay --debug --port 8090
else
  cp -r ./../shared ./

  gcloud functions deploy pay \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars STRIPE_API_KEY=$STRIPE_KEY
fi