# I.M. Hayhurst 2020 06 30

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    current_app,
    Response,
    flash,
    url_for,
)
import flask
from flask_mail import Message
import json
import redis
import markdown
from datetime import datetime as dt
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import pickle
import pandas as pd
import os
import ssl

# Application imports direct or via celery tasks
from ..HPCapps import uqueue
from ..HPCapps import inventory_load_host
from ..HPCapps import patching_load_host
from ..HPCapps import tasks
from ..HPCapps import inventory_style
from ..extensions import mail

website = Blueprint(
    "website",
    __name__,
    static_folder="static",
    static_url_path="/website/static",
    template_folder="templates",
)

flaskVer = flask.__version__
redis_url = "redis://:redis:6379/0"
r = redis.StrictRedis(host="redis", port=6379, db=0)

ssl._create_default_https_context = ssl._create_unverified_context

@website.route("/")
def index():
    # Open the README file
    with open(os.path.join(website.root_path) + "/Home.md", "r") as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        md = markdown.markdown(content, extensions=["tables", "fenced_code", "toc"])

    templateData = {
        "content": md,
        "flaskVer": flaskVer,
        "appver": current_app.config["APP_NAME"],
        "ldap_port": current_app.config["LDAP_PORT"],
        "home": os.path.join(current_app.config["UPLOAD_PATH"], "wibble"),
    }
    return render_template("index.html", **templateData)


@website.route("/cmdb")
def cmdb():
    data = pd.read_json('http://nginx:/api/cmdb')
    data.fillna('', inplace=True)
    data = inventory_style.applyTableStyle(data).render()
    templateData = {"content": data}
    return render_template("cmdb.html", **templateData), 201


@website.route("/queue")
def queue():
    gridjobs = uqueue.getGrid()
    jobhistory = uqueue.getGridHistory()
    return render_template("queue.html", gridjobs=gridjobs, jobhistory=jobhistory)


@website.route("/inventory/<hostname>", methods=["GET", "POST"])
def inventory_host(hostname):
    invdf = inventory_load_host.getInventoryDetail(hostname)
    patchdf = patching_load_host.getPatchingDetail(hostname)
    patchdf = inventory_style.applyTableStyle(patchdf).render()
    templateData = {
        "title": f"Inventory page for {hostname}",
        "hostname": hostname,
        "data": invdf,
        "patching": patchdf,
    }
    return render_template("inventory_host.html", **templateData)


@website.route("/notes/<hostname>", methods=["GET", "POST"])
def notes_host(hostname):
    path = r"/data/notes/"
    filename = f"{path}{hostname}.md"
    with open(filename, "r") as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        md = markdown.markdown(
            content,
            extensions=["tables", "fenced_code", "toc", "codehilite", "admonition"],
        )

    templateData = {
        "title": f"Operational notes for {hostname}",
        "content": md,
        "hostname": hostname,
    }
    return render_template("notes.html", **templateData)


@website.route("/showpatching")
def patching():
    title = "GBJH Linux Patching Status"
    # job.id passed to template so job data loaded by javascript
    job = tasks.getQueuedPatching.delay()
    now = dt.now()
    timeString = now.strftime("%A, %d %b %Y %H:%M:%S")
    templateData = {"JOBID": job.id, "title": title, "timeString": timeString}
    return render_template("patching.html", **templateData)


@website.route("/inventory")
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


@website.route("/distropie")
def distropie():
    b64pierelease = r.get("pie_release.png")
    b64pierelease = b64pierelease.decode("utf-8")
    return render_template("distropie.html", image=b64pierelease)


@website.route("/scatter")
def scatter():
    b64pierelease = r.get("scatter_patching.png")
    b64pierelease = b64pierelease.decode("utf-8")
    return render_template("scatterpatch.html", image=b64pierelease)


@website.route("timeline_upload", methods=["GET", "POST"])
def uploader():
    if request.method == "GET":
        return render_template("timeline_upload.html")

    elif request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash(f"{filename} Loaded", "info")
            df = pd.read_csv(file)
            pickled_df = pickle.dumps(df)
            # file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))
            job = tasks.processProjectlist.apply_async(
                kwargs={"filename": pickled_df}, serializer="pickle"
            )
        return render_template("timeline.html", JOBID=job.id)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["UPLOAD_EXTENSIONS"]
    )


@website.route("/timeline")
def timeline():
    b64timeline = r.get("timeline.png")
    b64timeline = b64timeline.decode("utf-8")
    return render_template("timeline.html", image=b64timeline)


@website.route("/webhook", methods=["POST"])
def respond():
    data = request.json
    sender = urlparse(request.host).path
    if data["object_kind"] == "pipeline" and data["builds"][0]["status"] == "success":
        build_id = data["builds"][0]["id"]
        user_email = data["builds"][0]["user"]["email"]
        web_url = data["project"]["web_url"]
        msg = Message(
            "Pipeline artefacts available for download",
            sender=f"<root@{sender}>",
            recipients=[f"{user_email}"],
        )
        msg.body = f""" Your pipeline has new artefacts available {web_url}/-/jobs/{build_id}/artifacts/download?file_type=archive
                    User: {user_email}
                    """
        mail.send(msg)
    else:
        print(
            " Build has no artefacts or recieved webhook we don't know what to do with"
        )

    return Response(status=200)
