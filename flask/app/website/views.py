# I.M. Hayhurst 2020 06 30

from flask import Flask, render_template
from flask import Blueprint
import flask
import pandas as pd

# Application imports
from ..HPCapps import uqueue
from ..HPCapps import patching_load
from ..HPCapps import inventory_load_host
from ..HPCapps import structures_api

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


@website.route("/showpatching")
def patching():
    df = patching_load.getPatching()
    styledPatchingTable = applyTableStyle(df)
    return render_template("patching.html", data=styledPatchingTable)


def applyTableStyle(df):

    styles = [
        hover(),
        dict(
            selector="th",
            props=[
                ("font-size", "110%"),
                ("text-align", "left"),
                ("text-transform", "capitalize"),
                ("background-color", "#000033"),
            ],
        ),
        dict(selector="caption", props=[("caption-side", "bottom")]),
        dict(selector="td a", props=[("display", "block")]),
    ]
    patchingStyle = (
        df.style.applymap(colorGrade, subset=["last-update", "boot-time", "days-pending"])
        .apply(oldscandate, axis=1)
        .set_table_styles(styles)
        .set_properties(subset=["owner"], **{"width": "300px"})
        .set_properties(subset=["release"], **{"width": "150px"})
        .hide_index()
        .format({"hostname": make_clickable})
        .set_precision(0)
        .render()
    )
    return patchingStyle


def hover(hover_color="#000033"):
    return dict(selector="tr:hover", props=[("background-color", "%s" % hover_color)])


def colorGrade(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for timedelta over specified
    strings, black otherwise.
    """
    patchingCritical = 60
    patchingUrgent = 50
    if val >= patchingCritical:
        color = "red"
    elif val >= patchingUrgent:
        color = "orange"
    else:
        color = "white"
    return f"color: {color}"


def oldscandate(s):
    """
    Takes a scalar and returns string for each column [8]
    the css property `'color: rgba(r,g,b,alpha)'` for scandate >2
    otherwise empty string '' for each column [8]
    """
    if s["last-scan"] >=2:
        return ['color: rgba(0,0,0,0.2)']*8
    else:
        return ['']*8


def make_clickable(val):
    return f'<a href="/inventory/{val}">{val}</a>'


@website.route("/inventory/<hostname>", methods=["GET", "POST"])
def inventory_host(hostname):
    para1 = hostname
    # d = inventory_load_host.gitInventoryHost(hostname)
    d = inventory_load_host.fileInventoryHost(hostname)
    # df = pd.json_normalize(d['contacts'], errors='ignore')
    df = pd.json_normalize(d, errors="ignore")
    return render_template("inventory_host.html", para1=para1, data=df.to_html())


@website.route("/structures")
def structuresapi():
    data = structures_api.getStructuresApi()
    df = pd.json_normalize(data, errors="ignore")
    return render_template("inventory_host.html", para1="wibble", data=df.to_html())
