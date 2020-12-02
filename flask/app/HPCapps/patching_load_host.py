"""
Load a list of patches pending for a host into a dataframe
group by repository
"""
import json
import pandas as pd

def getPatchingDetail(host):
    data = filePatchingHost(host)
    df = normaliseToDataframe(data)
    return df


def filePatchingHost(host):
    """
    Call from route to load pending patch detailfor named host from filesystem
    """
    path = r"/data/patching/"
    filename = f"{path}{host}.json"
    with open(filename) as json_file:
        try:
            data = json.load(json_file)
        except ValueError:
            print(f"Dodgy JSON mate aint it =={filename}==")
    return data


def normaliseToDataframe(data):
    """
    parse update-candidates JSON data to dataframe
    """
    df = pd.json_normalize(data["update-candidates"], meta=["rpm", "repo", "release"], errors="ignore")
    return df