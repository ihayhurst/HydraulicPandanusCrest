# I.M. Hayhurst 2020 06 30

import os
from flask import Flask, render_template
import flask
import datetime
import pandas as pd

from bs4 import BeautifulSoup
# Application imports
import HPCapps.uqueue
import HPCapps.patching_load
import HPCapps.inventory_load_host
import HPCapps.structures_api


app = Flask(__name__)
flaskVer = flask.__version__


@app.route('/') # Needs a landing page about HPC
def index():
    return render_template('index.html', flaskVer=flaskVer)

@app.route('/queue')
def queue():
    gridjobs = HPCapps.uqueue.getGrid()
    jobhistory =HPCapps.uqueue.getGridHistory()
    return render_template('queue.html', gridjobs=gridjobs, jobhistory=jobhistory)

@app.route('/queue-xml') # No menu link yet as experimental
def queuexml():
    gridjobs =HPCapps.uqueue.getGridXML()
    soup = BeautifulSoup(gridjobs, 'xml')
    return render_template('queue.html', gridjobs=gridjobs, jobhistory=None)


@app.route('/showpatching')
def patching():
    df = HPCapps.patching_load.getPatching()
    styledPatchingTable = applyTableStyle(df)
    return render_template('patching.html', data=styledPatchingTable)


def applyTableStyle(df):

    styles = [
              hover(),
              dict(selector="th", props=[("font-size", "110%"),
                   ("text-align", "left"), ("text-transform", "capitalize"),
                   ("background-color", "#000033")]),
              dict(selector="caption", props=[("caption-side", "bottom")]),
              dict(selector="td a", props=[("display", "block")])
              ]
    patchingStyle = (df.style.applymap(colorGrade, subset=['last-update', 'boot-time'])
                     .set_table_styles(styles)
                     .set_properties(subset=['owner'], **{'width': '300px'})
                     .set_properties(subset=['release'], **{'width': '150px'})
                     .hide_index()
                     .format({'hostname': make_clickable})
                     .set_precision(0)
                     .render())
    return patchingStyle

def hover(hover_color="#000033"):
    return dict(selector="tr:hover",
                props=[("background-color", "%s" % hover_color)])


def colorGrade(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for timedelta over specified
    strings, black otherwise.
    """
    patchingCritical = 60
    patchingUrgent = 50
    if (val >= patchingCritical):
        color = 'red'
    elif (val >= patchingUrgent):
        color = 'orange'
    else:
        color = 'white'
    return f'color: {color}'

def make_clickable(val):
    #return '<a target="_blank" href="/inventory/{}">{}</a>'.format(val,val)
    return '<a href="/inventory/{}">{}</a>'.format(val,val)

@app.route('/inventory/<hostname>', methods=['GET', 'POST'])
def inventory_host(hostname):
    para1 = hostname
    d = HPCapps.inventory_load_host.getInventoryHost(hostname)
    #df = pd.json_normalize(d['contacts'], errors='ignore')
    df = pd.json_normalize(d, errors='ignore')
    return render_template("inventory_host.html", para1=para1, data=df.to_html())

@app.route('/structures')
def structuresapi():
    data =HPCapps.structures_api.getStructuresApi()
    df = pd.json_normalize(data, errors='ignore')
    return render_template('inventory_host.html', para1='wibble', data=df.to_html())

 
@app.route('/file')
def file_out():
    flaskVer = os.listdir()
    with open('tmp/foobar', 'w+') as f:
        f.write(f'hello world:{flaskVer}')
    return render_template('index.html', flaskVer=flaskVer)
