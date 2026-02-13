#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

PAUSE=5
INSTANCE_NAME=`hostname`
echo "Instance is $INSTANCE_NAME"

# Get the instance zone from the GCE metadata server. This is faster than 'gcloud list'.
ZONE_FULL=$(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google")
if [[ -z "$ZONE_FULL" ]]; then
    echo "Error: Failed to retrieve instance zone from metadata server." >&2
    echo "This script should be run on a GCE VM." >&2
    exit 1
fi
# The zone is returned as 'projects/PROJECT_NUMBER/zones/ZONE'. We extract the last part.
ZONE=$(basename "$ZONE_FULL")
echo "Instance zone: $ZONE"

SUSPEND_COMMAND="gcloud compute instances suspend $INSTANCE_NAME --zone $ZONE"
echo "Suspend command is $SUSPEND_COMMAND"
echo "Suspending this instance in $PAUSE seconds unless you cancel with [CTRL-C]"
sleep $PAUSE
read -r -p "Are you sure? [y/N] " response
response=`echo "$response" | tr '[:upper]' '[:lower]'`
if [[ $response =~ ^y(es)?$ ]]; then
	`$SUSPEND_COMMAND`
else
    echo "Suspend operation cancelled."
fi
