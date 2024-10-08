#!/bin/bash

# chmod +x s3_env_vars.sh
# . ./s3_env_vars.sh 	This will set the env variables for all shells

export 	AWS_ENDPOINT_URL="http://localhost:9000" \
		AWS_ACCESS_KEY_ID="admin" \
		AWS_SECRET_ACCESS_KEY="admin12345" \
		AWS_BUCKET_NAME="data"
