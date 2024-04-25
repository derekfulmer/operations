#!/usr/bin/env python3

import argparse
import boto3
import json
from datetime import datetime


def arg_parse():
    """
    Defines arguments for user input
    """
    parser = argparse.ArgumentParser(
        prog="Parmeter Store Snapshot", description="Snapshots AWS SSM Parameter Store Parameters."
    )
    parser.add_argument(
        "--ns",
        "--namespace",
        action="store",
        dest="namespace",
        help="The namespace string used to fetch specific parameter paths.",
        required=False,
        type=str
    )
    parser.add_argument(
        "--env",
        "--environment",
        action="store",
        dest="environment",
        help="The deployment environment.",
        required=True,
        type=str
    )
    args = parser.parse_args()
    return args

def build_filename(fargs=None):
    now = datetime.now().strftime("%Y%m%d")
    if fargs.namespace == "/ztmesh":
        now_str = f"ztmesh_parameters_{fargs.environment}_{now}.json"
    else:
        now_str = f"ztmesh_parameters_{fargs.namespace}_{now}.json"
    return now_str

def get_all_parameters(fargs=None):
    client = boto3.client('ssm')
    paginator = client.get_paginator('get_parameters_by_path')

    if not fargs.namespace == "/namespace":
        path = f"/namespace/{fargs.namespace}"
    else:
        path = "/namespace"

    file = build_filename(fargs=fargs)
    parameters = []
    for page in paginator.paginate(Path=path, WithDecryption=True, Recursive=True):
            for parameter in page['Parameters']:
                res = dict((k, parameter[k]) for k in ['Name', 'Value'] if k in parameter)
                parameters.append(res)
    with open(file, 'w', encoding='utf-8') as j:
        json.dump(parameters, j, indent=1)
    return file

def upload_to_s3(fargs=None):
    client = boto3.client('s3')
    file_to_upload = get_all_parameters(fargs=fargs)

    bucket = f"account-storage-bucket"
    client.upload_file(file_to_upload, bucket, file_to_upload)

def main(fargs=None):
    args = arg_parse()
    get_all_parameters(fargs=args)
    upload_to_s3(fargs=args)

if __name__ == '__main__':
    main()
