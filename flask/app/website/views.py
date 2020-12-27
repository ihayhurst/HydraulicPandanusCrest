# I.M. Hayhurst 2020 06 30

from flask import Flask, render_template, request, current_app
from flask import Blueprint
import flask
import json
from datetime import datetime as dt
# Application imports direct or via celery tasks
from ..HPCapps import uqueue
from ..HPCapps import inventory_load_host
from ..HPCapps import patching_load_host
from ..HPCapps import tasks
from ..HPCapps import inventory_style

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
    return render_template("index.html", flaskVer=flaskVer, appver=current_app.config['APP_NAME']) 


@website.route("/queue")
def queue():
    gridjobs = uqueue.getGrid()
    jobhistory = uqueue.getGridHistory()
    return render_template("queue.html", gridjobs=gridjobs, jobhistory=jobhistory)


@website.route("/inventory/<hostname>", methods=["GET", "POST"])
def inventory_host(hostname):
    title = f"Inventory page for {hostname}"
    invdf = inventory_load_host.getInventoryDetail(hostname)
    patchdf = patching_load_host.getPatchingDetail(hostname)
    patchdf = inventory_style.applyTableStyle(patchdf).render()
    return render_template(
        "inventory_host.html",
        title=title,
        hostname=hostname,
        data=invdf,
        patching=patchdf,
    )


@website.route("/showpatching")
def patching():
    title = "GBJH Linux Patching Status"
    # job.id passed to template so job data loaded by javascript
    job = tasks.getQueuedPatching.delay()
    now = dt.now()
    timeString = now.strftime("%A, %d %b %Y %H:%M:%S")
    templateData = {
        'JOBID': job.id,
        'title': title,
        'timeString': timeString
        }
    return render_template("patching.html", **templateData)


@website.route("/allinventory")
def inventory_all():
    title = "GBJH Linux Inventory"
    job = tasks.getQueuedInventory.delay()
    return render_template("inventory.html", JOBID=job.id, title=title)


@website.route("/progress")
def progress():
    """
    Get the progress of our task and return it using a JSON object
    """
    jobid = request.values.get("jobid")
    if jobid:
        job = tasks.get_job(jobid)
        if job.state == "PROGRESS":
            return json.dumps(
                dict(
                    state=job.state,
                    progress=job.result["current"] * 1.0 / job.result["total"],
                )
            )
        elif job.state == "SUCCESS":
            return json.dumps(
                dict(
                    state=job.state,
                    progress=1.0,
                )
            )
    return "{}"


@website.route("/patchresult")
def result():
    """
    Pull our generated .png binary from redis and return it
    """
    jobid = request.values.get("jobid")
    if jobid:
        job = tasks.get_job(jobid)
        return job.result
    else:
        return 404
