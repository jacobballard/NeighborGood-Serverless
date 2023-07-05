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



STRIPE_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/stripe_key.txt)
GEOCODING_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/google_maps_geocoding.txt)
source /Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/sql_db_config.txt

if $LAPTOP; then
    STRIPE_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/stripe_key.txt)
    GEOCODING_KEY=$(</Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/google_maps_geocoding.txt)
    source /Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/sql_db_config.txt
else
    ## Mac Mini:
    STRIPE_KEY=$(<$HOME/Desktop/neighborgood/stripe_key.txt)

    # Actual path...
    # /Users/jacobballard/Library/Mobile Documents/com~apple~CloudDocs/Desktop/neighborgood/stripe_key.txt
    GEOCODING_KEY=$(<$HOME/Desktop/neighborgood/google_maps_geocoding.txt)

    source $HOME/Desktop/neighborgood/sql_db_config.txt
fi
if $RUN_LOCALLY; then
    # Command to run locally using functions-framework
    # Copy contents from shared_local to shared
    cp -r ./../shared_local/* ./shared
    functions-framework --target create_product --debug --port 8084
else
    cp -r ./../shared ./

    gcloud functions deploy create_product \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars DB_USER=$DB_USER,DB_PASS=$DB_PASS,DB_NAME=$DB_NAME,INSTANCE_UNIX_SOCKET=$INSTANCE_UNIX_SOCKET
fi