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
else
  ## Mac Mini:
  STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)
fi

if $RUN_LOCALLY; then
  # Command to run locally using functions-framework
  # Copy contents from shared_local to shared
  export STRIPE_API_KEY=$STRIPE_KEY
  
  pip install -r requirements.txt
  cp -r ./../shared_local/* ./shared
  functions-framework --target stripe_webhook_payment_intent_succeeded --debug --port 8095
else
  cp -r ./../shared ./

  gcloud functions deploy stripe_webhook_payment_intent_succeeded \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars STRIPE_API_KEY=$STRIPE_KEY
fi