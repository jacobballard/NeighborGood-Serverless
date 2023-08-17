#!/bin/zsh
RUN_LOCALLY=false
LAPTOP=false

# Loop through arguments
for arg in "$@"
do
    case $arg in
        --run_locally)
        RUN_LOCALLY=true
        shift # Remove --run_locally from processing
        ;;
        *)
        # shift # Remove generic argument from processing
        # ;;
    esac
    case $arg in
        --laptop)
        LAPTOP=true
        shift # Remove --run_locally from processing
        ;;
        *)
        # shift # Remove generic argument from processing
        # ;;
    esac
done




if $LAPTOP; then
  export LAPTOP=$LAPTOP
  STRIPE_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/stripe_key.txt)
  TAXCLOUD_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/taxcloud_key.txt)
  TAXCLOUD_LOGIN=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/taxcloud_login.txt)
else
  ## Mac Mini:
  STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)
  TAXCLOUD_KEY=$(</Users/jacobballard/Desktop/neighborgood/taxcloud_key.txt)
  TAXCLOUD_LOGIN=$(</Users/jacobballard/Desktop/neighborgood/taxcloud_login.txt)
fi

if $RUN_LOCALLY; then
  # Command to run locally using functions-framework
  # Copy contents from shared_local to shared
  export STRIPE_API_KEY=$STRIPE_KEY
  export TAXCLOUD_LOGIN_ID=$TAXCLOUD_LOGIN
  export TAXCLOUD_API_KEY=$TAXCLOUD_KEY
#   export GEOCODING_KEY=$GEOCODING_KEY
  pip install -r requirements.txt
  cp -r ./../shared_local/* ./shared
  functions-framework --target finalize_payment --debug --port 8095
else
  cp -r ./../shared ./

  gcloud functions deploy finalize_payment \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars STRIPE_API_KEY=$STRIPE_KEY,TAXCLOUD_API_KEY=$TAXCLOUD_KEY,TAXCLOUD_LOGIN_ID=$TAXCLOUD_LOGIN
fi