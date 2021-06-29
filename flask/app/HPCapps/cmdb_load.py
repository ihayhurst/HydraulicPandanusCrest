import json
import pandas as pd
from boltons.iterutils import remap


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