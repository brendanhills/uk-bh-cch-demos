#!/bin/bash
PAUSE=5
INSTANCE_NAME=`hostname`
echo "Instance is $INSTANCE_NAME"
ZONE=`gcloud compute instances list --filter="name=('$INSTANCE_NAME')" --format 'csv[no-heading](zone)'`
echo "Zone is $ZONE"

SUSPEND_COMMAND="gcloud compute instances suspend $INSTANCE_NAME --zone $ZONE"
echo "Suspend command is $SUSPEND_COMMAND"
echo "Suspending this instance in $PAUSE seconds unless you cancel with [CTRL-C]"
sleep $PAUSE
read -r -p "Are you sure? [y/N] " response
response=`echo "$response" | tr '[:upper]' '[:lower]'`
if [[ $response =~ ^y(es)?$ ]]; then
	`$SUSPEND_COMMAND`
else
    echo "Suspend canceled"
fi
