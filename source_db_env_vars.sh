#!/bin/bash

# chmod +x source_db_env_vars.sh
# . ./source_db_env_vars.sh 	This will set the env variables for all shells

export 	SOURCE_DB_USERNAME="postgres" \
        SOURCE_DB_PASSWORD="mysecretpassword" \
        SOURCE_DB_HOST="localhost" \
        SOURCE_DB_PORT="5432" \
        SOURCE_DB_NAME="big-star-db" \
        SOURCE_DB_SCHEMA="public"