""" 
Loads all inventory hostname.json files in a directory into a dataframe
create a combined dataframe
return dataframe or JSON
"""
import sys
import pandas as pd
import json
import glob
from datetime import datetime as dt
from celery import current_task


import gevent


def getInventory():
    """
    Call from route to load json from directory of hostname.json files
    Fetch list of dataframes and pass to concatenation
    Return dataframe.
    """
    NTOTAL = 4
    update_task(0.5, NTOTAL)
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
    path = r"/data/inventory"
    all_files = glob.glob(path + "/*.json")
    li = []
    pool = gevent.pool.Pool(1000)
    li = pool.map(readDataFileToFrame, all_files)
    return li


def readDataFileToFrame(filename):
    """
    Read data file JSON into dataframe
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


def normaliseToDataframe(data):
    """"""
    df = pd.json_normalize(data, errors="ignore")
    return df


def concatToDataframe(li):
    """
    Take list of dataframes, concatenate
    Return single dataframe.
    """
    df = pd.concat(li, axis=0, ignore_index=True)
    return df


def processDataframe(df):
    print("processing")
    return df
