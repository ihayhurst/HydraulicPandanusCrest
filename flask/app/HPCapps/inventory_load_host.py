#!/usr/bin/env python3
import json
import requests

# import ssl
import base64
import pandas as pd
from .inventory_style import applyTableStyle

# private token authentication
# curl -k --header "PRIVATE-TOKEN: bvci5iEFxxUzt1WmUqxt" "https://gitlab.rt.intra/api/v4/projects/983/"
# Python needs the env var set to find the certs
REQUESTS_CA_BUNDLE = "/etc/pki/tls/certs/ca-bundle.crt"


def getInventoryDetail(host):
    """
    Call from route to:
    load inventory JSON from filesystem or git
    return dataframe
    """
    data = fileInventoryHost(host)
    df = normaliseToDataframe(data)
    return df


def fetchResponse(host):
    private_token = "bvci5iEFxxUzt1WmUqxt"
    head = {"PRIVATE-TOKEN": f"{private_token}"}
    item_url = f"https://gitlab.rt.intra/api/v4/projects/790/repository/files/inventory%2F{host}%2Ejson?ref=master"

    response = requests.get(item_url, headers=head, verify=REQUESTS_CA_BUNDLE)
    return response


# try block to add


def unpackResponse(response):
    dictionary = json.loads(response.content)
    # print(f'What we get :\n {dictionary}\n')
    packet = dictionary.get("content")
    packet = base64.b64decode(packet)
    packet = packet.decode("utf-8")
    # print(f'What we want:\n {packet}')
    # Finaly into a dict we can use
    newdict = json.loads(packet)
    return newdict


def gitInventoryHost(host):
    """
    Pull inventory data for named host from git repo
    """
    response = fetchResponse(host)
    data = unpackResponse(response)
    return data


def fileInventoryHost(host):
    """
    Load inventory data for named host from filesystem
    """
    data = None
    path = r"/data/inventory/"
    filename = f"{path}{host}.json"
    with open(filename) as json_file:
        try:
            data = json.load(json_file)
        except ValueError as err:
            logger.error(f"Dodgy JSON mate aint it =={filename}== has {err}")
        except FileNotFoundError:
            return None
    return data


def normaliseToDataframe(data):
    """
    Parse inventory JSON data to dataframe
    """
    record = pd.json_normalize(data)
    # drop the cols that need normalizing
    discard_cols = ["contacts", "networks", "categories"]
    record.drop([x for x in discard_cols], axis=1, inplace=True)
    if "hardware" in record.columns:
        hardware = record[["hardware"]].copy()
    else:
        hardware = None
    record = record[["id", "description"]]
    contacts = pd.json_normalize(data, "contacts")
    networks = pd.json_normalize(data, "networks")
    categories = pd.json_normalize(data, "categories")
    categories = categories.T
    html = applyTableStyle(record)
    html = html.set_properties(subset=["description"], **{"width": "100%"}).render()
    if hardware is not None:
        html = html + applyTableStyle(hardware).render()
    html = html + f"<h4>Contacts</h4>{applyTableStyle(contacts).render()}"
    html = html + f"<h4>Networks</h4>{applyTableStyle(networks).render()}"
    html = html + f"<h4>Categories</h4>{applyTableStyle(categories).render()}"
    return html
