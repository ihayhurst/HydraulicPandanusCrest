#!/usr/bin/env python3
# I.M. Hayhurst 2020 06 19
# /home/admin/inventory/data/patching/*.json files

"""
Load Patching files and create a summary dataframe

Can be called as a command line to proces json to dataframe
show head / tail and column stats
show any JSON files that are not valid

getPatching called as module from route
"""

import sys
import pandas as pd
import json
import glob
from datetime import datetime as dt
from celery.utils.log import get_task_logger
from celery import current_task
import gevent
import numpy as np


logger = get_task_logger(__name__)


def getPatching():
    """
    Call from route to load json from directory of hostname.json files
    Fetch list of dataframes and pass to concatenation
    Return dataframe.
    """
    NTOTAL = 4
    update_task(0.2, NTOTAL)
    li = loadDataFiles()
    update_task(1, NTOTAL)
    df = concatToDataframe(li)
    update_task(2, NTOTAL)
    df = processDataframe(df)
    update_task(3, NTOTAL)
    return df


def update_task(progress, NTOTAL):
    current_task.update_state(
        state="PROGRESS", meta={"current": progress, "total": NTOTAL}
    )
    return 999


def loadDataFiles():
    """
    Generate list of patching.json files
    Divide among pool threads
    Pool threads read json into dataframes
    return list of dataframe objects
    """
    path = r"/data/patching/"
    all_files = glob.glob(path + "*.json")
    li = []
    pool = gevent.pool.Pool(1000)
    li = pool.map(readDataFileToFrame, all_files)
    return li


def readDataFileToFrame(filename):
    """
    Read data file JSON into datadrame
    drop long list of patches
    return dataframe
    """
    data = None
    with open(filename) as json_file:
        try:
            data = json.load(json_file)
        except ValueError as err:
            logger.error(f"Dodgy JSON mate aint it =={filename}== has {err}")
        df = normaliseToDataframe(data)
    return df


def writeOut(data, filename):
    """present to debug"""
    out_filename = f"{filename}-corrections.json"
    out_file = open(out_filename, "w")
    json.dump(data, out_file, indent=6)
    out_file.close()
    return


def normaliseToDataframe(data):
    """"""
    df = pd.json_normalize(data, errors="ignore")
    # Drop long list of individual patches before concatenation
    df = df[
        df.columns.drop(list(df.filter(regex="update-candidates"))).drop("last-update")
    ]
    return df


def concatToDataframe(li):
    """
    Take list of dataframes, concatenate
    Return single dataframe.
    """
    df = pd.concat(li, axis=0, ignore_index=True)
    return df


def processDataframe(df):
    """
    Take dataframe, Munge dataframe.
    Return Munged Dataframe.
    """
    # If there is no date for pending patched set it to the last scan time
    df["first-update-detected-tiem"] = df["first-update-detected-time"].fillna(
        df["unixtime"], inplace=True
    )
    # Convert unixtime to datetime.
    df[["unixtime", "boot-time", "first-update-detected-time"]] = df[
        ["unixtime", "boot-time", "first-update-detected-time"]
    ].apply(pd.to_datetime, unit="s")

    # Drop hostname (FQDN) and use id as Hostname.
    if "hostname" in df.columns:
        df.drop(["hostname"], axis=1, inplace=True)

    # Calculate how long since patches have been available
    df["first-update-detected-time"] = df.apply(
        lambda row: dt.now() - row["first-update-detected-time"], axis=1
    )
    df["first-update-detected-time"] = df["first-update-detected-time"].dt.days
    df.rename(columns={"first-update-detected-time": "days-pending"}, inplace=True)

    # Calculate how long since last boot, Reduce resolution down to the day
    df["boot-time"] = df.apply(lambda row: dt.now() - row["boot-time"], axis=1)
    df["boot-time"] = df["boot-time"].dt.days

    # Add to critical list if boot time > 180 days
    filters =[(df["boot-time"] >=180), (df["boot-time"]<180)]
    values =["True", None]
    df["critical"] = np.select(filters, values)

    # Calculate how long since last scan
    df.rename(columns={"unixtime": "last-scan"}, inplace=True)
    df["last-scan"] = df.apply(lambda row: dt.now() - row["last-scan"], axis=1)
    df["last-scan"] = df["last-scan"].dt.days

    # Centos Release string
    df["release"].replace(
        to_replace=r"(CentOS).*(\s\d+)\.(\d+)(?:.).*",
        value=r"\1 \2.\3",
        regex=True,
        inplace=True,
    )

    # Trim off domain from host
    df["id"].replace(to_replace=r"([^.]*).*", value=r"\1", regex=True, inplace=True)

    # Tidy Owner field
    # remove list[] indicator from owner
    df["owner"] = df["owner"].astype(str).str[1:-1]

    # remove @domain from email
    df["owner"].replace(to_replace=r"(?=@)[^\']+", value=r"", regex=True, inplace=True)

    # remove single quotes
    df["owner"].replace(
        to_replace=r"\'+([^\']*)\'", value=r"\1", regex=True, inplace=True
    )

    # set Title Case
    df["owner"] = df["owner"].str.title()
    # replace . with space
    df["owner"] = df["owner"].str.replace(".", " ")

    # Jiggle colum order for output
    df.rename(columns={"id": "hostname"}, inplace=True)
    df.rename(columns={"update-candidate-summary": "updates"}, inplace=True)
    df = df[
        [
            "hostname",
            "release",
            "days-pending",
            "boot-time",
            "owner",
            "description",
            "updates",
            "critical",
            "last-scan",
        ]
    ].copy()
    # Sort by days since last patched
    df.sort_values(
        by=["last-scan","critical",  "days-pending", "boot-time"],
        ascending=[True, False, False, False],
        inplace=True,
    )
    return df


def aboutData(df):
    """Print properties and sample of dataframe."""

    print(f"type:{df.dtypes}")
    print(f"Shape:{df.shape}")
    print(df.columns)
    print(df.head(10))
    print(df.tail(10))
    return


def main(args=None):
    """
    Start here if run from command line
    """
    df = getPatching()
    aboutData(df)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except ValueError:
        print("Give me something to do")
        sys.exit(1)
