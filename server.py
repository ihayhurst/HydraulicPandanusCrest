import os, sys
from flask import Flask, request, render_template
import flask
from datetime import datetime as dt
import xml.etree.cElementTree as et

#Imports for plot test
import io
import random
from flask import Response
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure

#Application imports
from HPCapps.queue import getGrid

app = Flask(__name__)
flaskVer = flask.__version__

@app.route('/')
def index():
    return render_template('index.html', flaskVer=flaskVer)

@app.route('/showpatching')
def geneious():
    gen_result =  showpatching.getPatching()
    return
	
@app.route('/queue')
def queue():
    gridjobs = getGrid()
    #print(gridjobs)
    return render_template('queue.html', gridjobs=gridjobs)
    	

#@app.route('/plot.png')
#def plot_png():
#    fig = create_figure()
#    output = io.BytesIO()
#    FigureCanvas(fig).print_png(output)
#    return Response(output.getvalue(), mimetype='image/png')
#
#def create_figure():
#    fig = Figure()
#    axis = fig.add_subplot(1, 1, 1)
#    xs = range(100)
#    ys = [random.randint(1, 50) for x in xs]
#    axis.plot(xs, ys)
#    return fig
