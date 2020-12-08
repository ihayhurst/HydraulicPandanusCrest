""" 
TODO: load all inventory hostname.json files in a directory into a dataframe
create a summary dataframe
"""
import sys
import pandas as pd
import json
import glob
from datetime import datetime as dt
from billiard.pool import Pool


def getInventory():
    """
    Call from route to load json from directory of hostname.json files
    Fetch list of dataframes and pass to concatenation
    Return dataframe.
    """
    li = loadDataFiles()
    df = concatToDataframe(li)
    df = processDataframe(df)
    return df


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
    pool = Pool(4)
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
        except ValueError:
            print(f"Dodgy JSON mate aint it =={filename}==")
        df = normaliseToDataframe(data)
    return df


def normaliseToDataframe(data):
    """
    """
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