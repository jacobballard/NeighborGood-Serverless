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
  # STRIPE_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/stripe_key.txt)
else
  ## Mac Mini:
  # STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)
fi

if $RUN_LOCALLY; then
  # Command to run locally using functions-framework
  # Copy contents from shared_local to shared
  # export STRIPE_API_KEY=$STRIPE_KEY
  
  pip install -r requirements.txt
  cp -r ./../shared_local/* ./shared
  functions-framework --target trigger_firestore_cart_updated --signature-type event --debug --port 8101
else
  cp -r ./../shared ./

  gcloud functions deploy trigger_firestore_cart_updated \
  --runtime python310 \
  --region us-central1 \
  --trigger-event "providers/cloud.firestore/eventTypes/document.update" \
  --trigger-resource "projects/pastry-6b817/databases/(default)/documents/carts/{cartId}"
fi
