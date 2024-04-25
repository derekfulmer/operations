#!/usr/bin/env bash

datenow=$(date +%Y%m%d)
r53_file=ztmesh_route53_hostedzones_"$datenow".json
recordsets=ztmesh_route53_records_"$datenow".json

#Get hosted zones and their data
aws route53 list-hosted-zones > "$r53_file"

#Get hosted zone ids from file and set as array
declare -a ZONE_ARRAY
ZONE_ARRAY=$(grep "Id" $r53_file | tr -d '"' | tr -d ',' | tr -d '/' | sed -e 's/Id:\ //g' | sed 's/hostedzone//g' | tr -d ' \t')

for i in ${ZONE_ARRAY[@]}; do
    aws route53 list-resource-record-sets --hosted-zone-id "$i" >> "$recordsets"
done