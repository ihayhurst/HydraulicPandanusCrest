import os, sys
from flask import Flask, request, render_template
import flask
import datetime 
from bs4 import BeautifulSoup
import pandas as pd
import functools

#Application imports
from HPCapps.queue import *
from HPCapps.patching_load import *

app = Flask(__name__)
flaskVer = flask.__version__

@app.route('/')
def index():
    return render_template('index.html', flaskVer=flaskVer)

@app.route('/queue')
def queue():
    gridjobs = getGrid()
    jobhistory = getGridHistory()
    return render_template('queue.html', gridjobs=gridjobs, jobhistory=jobhistory)

@app.route('/queue-xml')
def queuexml():
    gridjobs = getGridXML()
    soup = BeautifulSoup(gridjobs, 'xml')
    return render_template('queue.html', gridjobs=gridjobs, jobhistory=None)

@app.route('/showpatching')
#@functools.lru_cache(maxsize=128, typed=False)
def patching():
    df = getPatching()
    #pd.set_option('colheader_justify', 'left')
    #df.style.format({"B": lambda x: "±{:.2f}".format(abs(x))})
    patchingStyle = (df.style.applymap(colorGrade, subset=['last-update', 'boot-time'])
                    .hide_index()
                    .render())
    #with open('tmp/patching-style', 'w+') as f:
        #f.write(patchingStyle)
    #return render_template('patching.html', data=df.to_html(index=False, border=0, justify='left'))
    
    return render_template('patching.html', data=patchingStyle)

def colorGrade(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for timedelta over specified
    strings, black otherwise.
    """
    #days = datetime.timedelta(days=1)
    #val = val.datetime.timedelta.days
    patchingCritical = 60
    patchingUrgent = 50
    if (val >= patchingCritical):
        color = 'red'
    elif (val >= patchingUrgent):
        color = 'orange'
    else:
        color = 'white'
    return f'color: {color}'

@app.route('/file')    	
def file_out():
    flaskVer = os.listdir()
    with open('tmp/foobar', 'w+') as f:
        f.write(f'hello world:{flaskVer}')
    return render_template('index.html', flaskVer=flaskVer)
