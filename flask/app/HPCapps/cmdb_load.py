import json
import pandas as pd

# from boltons.iterutils import remap


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
    df["Disk_space_GB"] = df["Disk_space_GB"].fillna(0.0).astype(int)
    df.fillna("", inplace=True)
    df.columns = df.columns.str.replace(" ", "_")
    df["OS_Version"] = df["OS_Version"].astype(str)
    df.sort_values(
        by=["IP_Address", "OS_Version"],
        ascending=[True, True],
        inplace=True,
    )
    data = df.to_dict(orient="records")
    # Create clean version with empty keys dropped
    data = dropEmptyKeys(data)
    return data


def dropEmptyKeys(d: dict):
    items = ((k, v) for k, v in d.items())
    return {k: v for k, v in items if v}
