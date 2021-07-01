import json
import pandas as pd
import boto3
from boltons.iterutils import remap
import datetime
from flask import current_app

# boto3
sess_params = {
            'aws_access_key_id': current_app.config.get('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': current_app.config.get('AWS_SECRET_ACCESS_KEY'),
            'region_name':  current_app.config.get("AWS_DEFAULT_REGION")
        }
session = boto3.session.Session(**sess_params)

def dump_date(thing):
    if isinstance(thing, datetime.datetime):
        return thing.isoformat()
    return thing

def getFlatInventory(host):
    """
    Call from route to:
    load inventory JSON from filesystem or git
    return dict
    """
    data = fileInventoryHost(host)
    df = normaliseToDataframe(data)
    data = processDataframe(df)
    return data

def get_Instances():
    result = {}
    #ec2 = boto3.resource('ec2', region_name=region_name)
    ec2client = session.client('ec2')
    data = ec2client.describe_instances()
    for reservation in data["Reservations"]:

    #data = ec2.instances.filter(Filters=[{'Name':'tag:Name'}])
    # data = ec2.instances
        for instance in reservation["Instances"]:
            #for tag in instance.tags:
                """      if 'Name' in tag['Key']:
                    name = tag['Value']
                ec2_info = {
                     "Name": name,
                     "Instance_Id": str(instance.id),
                     "State": instance.state["Name"],
                     "Private_IP": instance.private_ip_address,
                     }
             #data = json.dumps(ec2_info,indent=4,sort_keys=True )
            """
        #instance = dump_date(instance)
        data = json.dumps(instance, default=dump_date)
        #df = pd.json_normalize(data)
        #data = df.to_dict(orient="records")
        return data

def fileInventoryHost(host):
    """
    Load inventory data for named host from filesystem
    """
    filename = host
    data = None
    path = r"/data/cmdb/"
    filename = f"{path}{host}.json"
    with open(filename) as json_file:
        try:
            data = json.load(json_file)
        except ValueError as err:
            raise RuntimeError(
                f"Dodgy JSON mate aint it =={filename}== has {err}"
            ) from err
        except FileNotFoundError:
            return None
    return data


def normaliseToDataframe(data):
    """
    Parse inventory JSON data to dataframe
    """
    df = pd.json_normalize(data)
    return df


def processDataframe(df):
    df.fillna("", inplace=True)
    # remove [] and single quotes
    df["IP Address"] = df["IP Address"].astype(str).str[1:-1]
    df["IP Address"].replace(
        to_replace=r"\'+([^\']*)\'", value=r"\1", regex=True, inplace=True
    )
    # df.rename(columns={"id": "hostname"}, inplace=True)
    data = df.to_dict(orient="records")
    # Create clean version with empty keys dropped
    data = dropEmptyKeys(data)
    return data


def dropEmptyKeys(dict):
    drop_falsey = lambda path, key, value: bool(value)
    clean = remap(dict, visit=drop_falsey)
    return clean
