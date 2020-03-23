import os, sys
from flask import Flask, request, render_template
import flask
from datetime import datetime as dt

app = Flask(__name__)
flaskVer = flask.__version__

@app.route('/')
def index():
    return render_template('index.html', flaskVer=flaskVer)

@app.route('/showpatching')
def geneious():
    gen_result =  showpatching.getPatching()
	
	
