#!/usr/bin/env python3
import json
import requests

# import ssl
# import base64

# private token authentication
# curl -k --header "PRIVATE-TOKEN: bvci5iEFxxUzt1WmUqxt" "https://gitlab.rt.intra/api/v4/projects/983/"
# Python needs the env var set to find the certs
REQUESTS_CA_BUNDLE = "/etc/pki/tls/certs/ca-bundle.crt"


def fetchResponse():
    # private_token = 'bvci5iEFxxUzt1WmUqxt'
    # head = {'PRIVATE-TOKEN': f'{private_token}'}
    item_url = f"http://gbjhvice081.eame.syngenta.org/api/structures/?format=json"

    response = requests.get(item_url)
    return response


def unpackResponse(response):
    dictionary = json.loads(response.content)
    return dictionary


def getStructuresApi():
    response = fetchResponse()
    data = unpackResponse(response)
    return data
