#!/bin/sh

regions=$(cat regions.json | jq -r '.[]')

for region in $regions ; do
    ./put-alarms.sh $region
done