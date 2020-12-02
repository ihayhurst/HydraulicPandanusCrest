# I.M. Hayhurst 2020 06 30

from flask import Flask, render_template, request
from flask import Blueprint
import flask
import json
import pandas as pd

# Application imports direct or via celery tasks
from ..HPCapps import uqueue
from ..HPCapps import inventory_load_host
from ..HPCapps import patching_load_host
from ..HPCapps import tasks

website = Blueprint(
    "website",
    __name__,
    static_folder="static",
    static_url_path="/website/static",
    template_folder="templates",
)

app = Flask(__name__)
flaskVer = flask.__version__


@website.route("/")  # Needs a landing page about HPC
def index():
    return render_template("index.html", flaskVer=flaskVer)


@website.route("/queue")
def queue():
    gridjobs = uqueue.getGrid()
    jobhistory = uqueue.getGridHistory()
    return render_template("queue.html", gridjobs=gridjobs, jobhistory=jobhistory)


@website.route("/inventory/<hostname>", methods=["GET", "POST"])
def inventory_host(hostname):
    para1 = hostname
    title = f"Inventory page for {hostname}"
    d = inventory_load_host.fileInventoryHost(hostname)
    # df = pd.json_normalize(d['contacts'], errors='ignore')
    df = pd.json_normalize(d, errors="ignore")
    patchingData = patching_load_host.getPatchingDetail(hostname)
    # TODO append call to generate list of patches pending for host
    return render_template("inventory_host.html", title=title, para1=para1, data=df.to_html(), patching=patchingData.to_html())


@website.route("/showpatching")
def patching():
    title = "GBJH Linux Patching Status"
    job = tasks.getQueuedPatching.delay()
    return render_template("patching.html", JOBID=job.id, title=title)


@website.route('/progress')
def progress():
    '''
    Get the progress of our task and return it using a JSON object
    '''
    jobid = request.values.get('jobid')
    if jobid:
        job = tasks.get_job(jobid)
        if job.state == 'PROGRESS':
            return json.dumps(dict(
                state=job.state,
                progress=job.result['current']*1.0/job.result['total'],
            ))
        elif job.state == 'SUCCESS':
            return json.dumps(dict(
                state=job.state,
                progress=1.0,
            ))
    return '{}'


@website.route('/patchresult')
def result():
    '''
    Pull our generated .png binary from redis and return it
    '''
    jobid = request.values.get('jobid')
    if jobid:
        job = tasks.get_job(jobid)
        return job.result
    else:
        return 404

