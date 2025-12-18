#!/bin/bash
cd ./deployment/mcp-toolbox/
if [ -e ./toolbox ]
then
    	echo "toolbox found"
else
	echo "Installing toolbox"
	export VERSION=0.23.0
	curl -L -o toolbox https://storage.googleapis.com/genai-toolbox/v$VERSION/linux/amd64/toolbox
	chmod +x toolbox
fi
export DB_USER=postgres
export DB_PASS=$(gcloud secrets versions access latest --secret=db-password)

./toolbox --tools-file tools.yaml --log-level DEBUG --allowed-origins=127.0.0.1 --port=5000
