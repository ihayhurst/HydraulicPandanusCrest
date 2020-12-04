#!/usr/bin/env python3
import json
import requests
import ssl
import base64
import pandas as pd

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
    path = r"/data/inventory/"
    filename = f"{path}{host}.json"
    with open(filename) as json_file:
        try:
            data = json.load(json_file)
        except ValueError:
            print(f"Dodgy JSON mate aint it =={filename}==")
    return data


def normaliseToDataframe(data):
    """
    parse inventory JSON data to dataframe
    """
    df = pd.json_normalize(data, errors="ignore")
    return df 
