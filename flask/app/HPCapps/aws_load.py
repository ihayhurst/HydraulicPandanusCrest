import pandas as pd
import boto3
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
    )[["State.Name", "PrivateIpAddress", "InstanceType", "Tags"]]
    tags = list(df["Tags"])
    df_tags = untangleTags(tags)
    df.drop(["Tags"], axis=1, inplace=True)
    df = pd.concat([df, df_tags], axis=1)
    df.OwnerEmail = (
        df.OwnerEmail.str.replace(".", " ").str.replace("_", " ").str.title()
    )
    df.ContactEmail = (
        df.ContactEmail.str.replace(".", " ").str.replace("_", " ").str.title()
    )
    df.OwnerEmail.replace(r"@.*?$", "", regex=True, inplace=True)
    df.ContactEmail.replace(r"@.*?$", "", regex=True, inplace=True)
    df = df[
        [
            "State.Name",
            "Name",
            "PrivateIpAddress",
            "InstanceType",
            "OwnerEmail",
            "ContactEmail",
            "OS",
            "Application",
            "Purpose",
            "CostCenter",
            "ProjectNumber",
            "AWS-Backup",
            "AvailabilityGroup",
            "PatchGroup",
        ]
    ]
    df.sort_values(
        by=["Application", "OS"],
        ascending=[True, True],
        inplace=True,
    )
    data = df.to_dict(orient="records")
    return data


def untangleTags(df):
    li = []
    for item in df:
        keys = []
        values = []
        for dicts in item:
            keys.append(dicts.get("Key"))
            values.append(dicts.get("Value"))
        df = pd.DataFrame([values], columns=keys)
        li.append(df)

    df = pd.concat(li, axis=0, ignore_index=True)
    df = df[
        [
            "Name",
            "ContactEmail",
            "CostCenter",
            "OwnerEmail",
            "AWS-Backup",
            "OS",
            "ProjectNumber",
            "AvailabilityGroup",
            "Application",
            "Purpose",
            "PatchGroup",
        ]
    ]
    return df
