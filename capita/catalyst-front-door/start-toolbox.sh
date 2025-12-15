#!/bin/sh
#gcert
cd ./deployment/mcp-toolbox/
./toolbox --tools-file tools.yaml --log-level DEBUG
#./cloud-sql-proxy uk-bh-experiments-argolis:us-central1:software-assistant --debug-logs
