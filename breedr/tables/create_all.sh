#!/bin/bash

for csv_file in animals.csv
do
    echo $csv_file
    if test "$( wc -l < "$csv_file")" -eq  "1" 
    then
       echo "wc -l $csv_file - skipping"
    else
        tablename="${csv_file%.*}"
         echo creating table $tablename for $csv_file

          command="bq --location=us-east1 load --source_format=CSV --autodetect breedr.$tablename gs://uk-bh-experiments-argolis-us/breedr/tables/$csv_file"
          echo $command
          bq
    fi
done
