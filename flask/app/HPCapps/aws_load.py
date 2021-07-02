import json
import pandas as pd
import boto3
from boltons.iterutils import remap
import datetime
from flask import current_app

# boto3
sess_params = {
    "aws_access_key_id": current_app.config.get("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": current_app.config.get("AWS_SECRET_ACCESS_KEY"),
    "region_name": current_app.config.get("AWS_DEFAULT_REGION"),
}
session = boto3.session.Session(**sess_params)


def dump_date(thing):
    if isinstance(thing, datetime.datetime):
        return thing.isoformat()
    return thing


def get_Instances():
    ec2client = session.client("ec2")
    response = ec2client.describe_instances()
    df = pd.json_normalize(
        pd.DataFrame(
            pd.DataFrame(response["Reservations"])
            .apply(lambda r: r.str[0])
            .Instances.values
        )[0]
    )[["ImageId", "PrivateIpAddress", "InstanceType", "State.Name", "Tags"]]
    # df["Name"] = df.Tags.apply( lambda r: r[0]["Value"])
    df["Name"] = df.Tags.apply( lambda r: r[0]["Value"] if r[0]["Key"]== "Name" else "Untagged")
    # df.drop(["Tags"], axis=1, inplace=True)
    data = df.to_dict(orient="records")
    return data

def nameTag(df): # not used yet
    for dicts in df:
        next(item for item in dicts if item["Key"] == "Name")
    
    return 