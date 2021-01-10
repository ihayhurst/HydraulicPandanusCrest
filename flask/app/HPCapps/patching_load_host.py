"""
Load a list of patches pending for a host into a dataframe
group by repository
"""
import json
import pandas as pd


def getPatchingDetail(host):
    data = filePatchingHost(host)
    df = normaliseToDataframe(data)
    df = processDataFrame(df)
    return df


def filePatchingHost(host):
    """
    Call from route to load pending patch detailfor named host from filesystem
    """
    path = r"/data/patching/"
    filename = f"{path}{host}.json"
    data = None
    with open(filename) as json_file:
        try:
            data = json.load(json_file)
        except ValueError as err:
            logger.error(f"Dodgy JSON mate aint it =={filename}== has {err}")
    return data


def normaliseToDataframe(data):
    """
    parse update-candidates JSON data to dataframe
    """
    df = pd.json_normalize(data["update-candidates"],  errors="ignore")
    return df


def processDataFrame(df):
    """
    Take dataframe as input, munge data to taste
    Return munged dataframe
    """
    # Sort by repo
    if 'repo' in df.columns:
        df.sort_values(by=["repo"], ascending=True, inplace=True)
    return df
