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


# Read Stripe secret key from file

if $LAPTOP; then
    source /Users/jacobballard/Library/Mobile\ Documents/com~apple~CloudDocs/Desktop/neighborgood/sql_db_config.txt
else
    source $HOME/Desktop/neighborgood/sql_db_config.txt
fi
if $RUN_LOCALLY; then
    # Command to run locally using functions-framework
    # Copy contents from shared_local to shared
    pip install -r requirements.txt
    cp -r ./../shared_local/* ./shared
    functions-framework --target get_products --debug --port 8083
else
    # Command to deploy to gcloud
    cp -r ./../shared ./
    gcloud functions deploy get_products \
      --runtime python310 \
      --trigger-http \
      --allow-unauthenticated \
      --set-env-vars DB_USER=$DB_USER,DB_PASS=$DB_PASS,DB_NAME=$DB_NAME,INSTANCE_UNIX_SOCKET=$INSTANCE_UNIX_SOCKET
fi
