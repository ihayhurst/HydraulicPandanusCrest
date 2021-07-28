import json
import pandas as pd
from .inventory_style import applyTableStyle


def getInventoryDetail(host):
    """
    Call from route to:
    load inventory JSON from filesystem or git
    return dataframe
    """
    data = fileInventoryHost(host)
    df = normaliseToDataframe(data)
    return df


def fileInventoryHost(host):
    """
    Load inventory data for named host from filesystem
    """
    data = None
    path = r"/data/config/"
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
