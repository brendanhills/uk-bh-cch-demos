#!/bin/bash

#gcert
if [ -e ./cloud-sql-proxy ]
then
    	echo "cloud-sql-proxy found"
else
    	echo "Installing cloud-sql-proxy"
	curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.20.0/cloud-sql-proxy.linux.amd64
	chmod +x cloud-sql-proxy
fi
./cloud-sql-proxy uk-bh-experiments-argolis:us-central1:software-assistant --debug-logs
#lsof -i:5432
