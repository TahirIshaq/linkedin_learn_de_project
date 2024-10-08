#!/bin/bash

# chmod +x source_db_env_vars.sh
# . ./source_db_env_vars.sh 	This will set the env variables for all shells

export 	DESTINATION_DB_USERNAME="test" \
        DESTINATION_DB_PASSWORD="test" \
        DESTINATION_DB_HOST="localhost" \
        DESTINATION_DB_PORT="5433" \
        DESTINATION_DB_NAME="test-db" \
        DESTINATION_DB_SCHEMA="public"