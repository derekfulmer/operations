#!/usr/bin/env python3

import argparse
import boto3
from pprint import pprint

r53 = boto3.client("route53")

def arg_parse():
    """
    Defines arguments for user input
    """
    parser = argparse.ArgumentParser(
        prog="dnstruck", description="Process Route53 Requests for an organization"
    )
    parser.add_argument(
        "--zone",
        action="store",
        dest="zone_name",
        help="The zone name; e.g. example.com.",
        type=str,
    )
    parser.add_argument(
        "--action",
        action="store",
        dest="action",
        help="The action to perform on the record.",
        type=str.upper,
        choices=["UPSERT", "DELETE", "READ"],
        required=True
    )
    parser.add_argument(
        "--value",
        action="store",
        dest="value",
        type=str.upper,
        help="Value of the record, (IP address or AWS resource.)",
        default="not_set"
    )
    parser.add_argument(
        "--type",
        action="store",
        dest="type",
        help="The type of record to be set: CNAME or A Record.",
        type=str.upper,
        choices=["CNAME", "A"],
        required=True
    )
    parser.add_argument(
        "--name",
        action="store",
        dest="name",
        type=str,
        help="The name of the entry before the zone name",
        required=True
    )
    parser.add_argument(
        "--ttl",
        action="store",
        dest="ttl",
        type=int,
        help="The Time To Live value in seconds; defaults to 300",
        default=300
    )
    args = parser.parse_args()
    return args


def get_hosted_zone_id(fargs=None):
    response = r53.list_hosted_zones_by_name(DNSName=fargs.zone_name)
    parsed_zone = response["HostedZones"][0]["Id"].strip("/hostedzone/")
    print(f"Zone ID: {parsed_zone}")
    return parsed_zone


def read_record(fargs=None):
    hosted_zone = get_hosted_zone_id(fargs)
    name = f"{fargs.name}.{fargs.zone_name}."
    response = r53.list_resource_record_sets(
        HostedZoneId=hosted_zone,
        StartRecordName=name,
        StartRecordType=fargs.type,
        MaxItems="1",
    )
    record = response["ResourceRecordSets"][0]
    return record


def create_record(fargs=None):
    hosted_zone = get_hosted_zone_id(fargs)
    name = f"{fargs.name}.{fargs.zone_name}."
    try:
        r53.change_resource_record_sets(
            HostedZoneId=hosted_zone,
            ChangeBatch={
                "Comment": "Adds a new record",
                "Changes": [
                    {
                        "Action": fargs.action,
                        "ResourceRecordSet": {
                            "Name": name,
                            "Type": fargs.type,
                            "TTL": fargs.ttl,
                            "ResourceRecords": [
                                {
                                    # The current or new DNS record value
                                    "Value": fargs.value
                                },
                            ],
                        },
                    },
                ],
            },
        )
        print(f"Upsert record: {name}")
    except Exception as error:
        print(error)


def delete_record(fargs=None):
    hosted_zone = get_hosted_zone_id(fargs)
    delete_name = f"{fargs.name}.{fargs.zone_name}."
    response = r53.list_resource_record_sets(
        HostedZoneId=hosted_zone, StartRecordName=delete_name, MaxItems="1"
    )
    print("Deleting: " + delete_name)

    record_to_delete = dict()
    record_to_delete["Name"] = "No record found"
    
    if delete_name in response["ResourceRecordSets"][0]["Name"]:
        record_to_delete = response["ResourceRecordSets"][0]
        print(record_to_delete)
        r53.change_resource_record_sets(
            HostedZoneId=hosted_zone,
            ChangeBatch={
                "Changes": [
                    {"Action": fargs.action, "ResourceRecordSet": record_to_delete}
                ]
            },
        )
    print("Deleted: " + record_to_delete["Name"])


def main():
    args = arg_parse()

    # Evaluate the action to take
    if args.action == "UPSERT":
        create_record(fargs=args)
    if args.action == "READ":
        pprint(read_record(fargs=args))
    if args.action == "DELETE":
        delete_record(fargs=args)


# Run main Code
if __name__ == "__main__":
    main()
