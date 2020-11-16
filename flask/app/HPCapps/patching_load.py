#!/usr/bin/env python3
# I.M. Hayhurst 2020 06 19
# /home/admin/patching/cache/*.json files

import sys
import pandas as pd
import json
import glob
from datetime import datetime as dt


def getPatching():
    """
    Fetch list of dataframes and pass to concatenation
    Return dataframe.
    """
    li = loadDataFiles()
    df = concatToDataframe(li)
    return df


def loadDataFiles():
    # path = r'/Users/ihayhurst/Google Drive/Code/python/cache'
    path = r"/data/patching"
    all_files = glob.glob(path + "/*.json")
    li = []

    for filename in all_files:
        with open(filename) as json_file:
            try:
                d = json.load(json_file)
            except ValueError:
                print(f"Dodgy JSON mate aint it =={filename}==")
                continue

            df = pd.json_normalize(d, errors="ignore")
            # Drop long list of individual patches before concatenation
            df = df[df.columns.drop(list(df.filter(regex="update-candidates")))]
            li.append(df)
    return li


def concatToDataframe(li):
    """
    Take list of dataframes, concatenate
    Return dataframe.
    """
    df = pd.concat(li, axis=0, ignore_index=True)
    # If there is no date for pending patched set it to the last scan time
    df["first-update-detected-tiem"] = df["first-update-detected-time"].fillna(
        df["unixtime"], inplace=True
    )
    # Convert unixtime to datetime.
    df[["unixtime", "boot-time", "last-update", "first-update-detected-time"]] = df[
        ["unixtime", "boot-time", "last-update", "first-update-detected-time"]
    ].apply(pd.to_datetime, unit="s")
    # Drop hostname (FQDN) and use id as Hostname.
    df.drop(["hostname"], axis=1, inplace=True)
    # Calculate how long since last update, show smallest unit as Days.
    df["last-update"] = df.apply(lambda row: dt.now() - row["last-update"], axis=1)
    df["last-update"] = df["last-update"].dt.days
    # Calculate how long since patches have been available
    df["first-update-detected-time"] = df.apply(
        lambda row: dt.now() - row["first-update-detected-time"], axis=1
    )
    df["first-update-detected-time"] = df["first-update-detected-time"].dt.days
    df.rename(columns={"first-update-detected-time": "days-pending"}, inplace=True)
    # Calculate how long since last boot, Reduce resolution down to the day
    df["boot-time"] = df.apply(lambda row: dt.now() - row["boot-time"], axis=1)
    df["boot-time"] = df["boot-time"].dt.days
    # Calculate how long since last scan
    df.rename(columns={"unixtime": "last-scan"}, inplace=True)
    df["last-scan"] = df.apply(lambda row: dt.now() - row["last-scan"], axis=1)
    df["last-scan"] = df["last-scan"].dt.days
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
    df = df[
        [
            "hostname",
            "release",
            "days-pending",
            "boot-time",
            "last-update",
            "owner",
            "description",
            "last-scan",
        ]
    ]
    # Sort by days since last patched
    df.sort_values(
        by=["last-scan", "days-pending", "boot-time"],
        ascending=[True, False, False],
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
