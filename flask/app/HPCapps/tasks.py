import redis
import pickle
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np
import base64
import io
import seaborn as sns
from boltons.iterutils import remap

from celery import Celery
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

# Application imports
from .patching_load import getPatching
from .patching_style import applyTableStyle
from .inventory_load import getInventory
from .inventory_style import applyTableStyle as applyInventoryStyle


# TODO load this from config
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"
# EXPIRATION_SECONDS = 600


redis_url = "redis://:redis:6379/0"
r = redis.StrictRedis(host="redis", port=6379, db=0)
# Initialize Celery
celery = Celery("worker", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
celery.conf.accept_content = ["json", "msgpack", "pickle"]
celery.conf.result_serializer = "pickle"
logger = get_task_logger(__name__)


def get_job(job_id):
    """
    To be called from our web app.
    The job ID is passed and the celery job is returned.
    """
    return AsyncResult(job_id, app=celery)


@celery.task(bind=True, hard_time_limit=6)
def getQueuedPatching(self):
    logger.info(self.request.id)
    logger.info("startung run")
    html = "<h3> Your task, young Padowan; failed it has.</h3>"
    df = None
    try:
        df = getPatching()
        # df.to_csv(r'/data/patching/patching.csv')
        logger.info("Make graphics")
        df_sum = summaryTable(df)
        fig = makePie(df_sum)
        figToRdis(fig, "pie_release.png")

        fig = makeScatter(df)
        figToRdis(fig, "scatter_patching.png")
        logger.info("ending run")
        html = applyTableStyle(df)
    except SoftTimeLimitExceeded:
        clean_up_in_a_hurry()
    return html


@celery.task(bind=True, hard_time_limit=6)
def getQueuedInventory(self):
    """
    get inventory df
    return html
    """
    logger.info(self.request.id)
    html = "<h3> Your task, young Padowan; failed it has.</h3>"
    df = None
    try:
        df = getInventory()
    except SoftTimeLimitExceeded:
        clean_up_in_a_hurry()
    html = applyInventoryStyle(df)
    html = html.set_table_attributes('class="fixedhead"').render()
    return html


@celery.task(bind=True, hard_time_limit=6)
def getQueuedInventoryJSON(self):
    """
    get inventory df
    return dict (let restful do the JSON conversion)
    """
    logger.info(self.request.id)
    try:
        df = getInventory()
    except SoftTimeLimitExceeded:
        clean_up_in_a_hurry()
    df.rename(columns={"id": "hostname"}, inplace=True)
    # df[pd.DataFrame(df.categories.tolist()).isin(selection).any(1).values]
    data = df.to_dict(orient="records")
    # Create clean version with empty keys dropped
    data = dropEmptyKeys(data)
    return data


@celery.task(bind=True, hard_time_limit=6)
def processProjectlist(self, *args, **kwargs):
    """Make df from uploaded timeline, return html of processed timeline"""
    self.update_state(state="PROGRESS", meta={"current": 1, "total": 3})
    filename = kwargs.get("filename")
    df = pickle.loads(filename)
    self.update_state(state="PROGRESS", meta={"current": 2, "total": 3})
    fig = timelineGraph(df)
    figToRdis(fig, "timeline.png")
    self.update_state(state="PROGRESS", meta={"current": 3, "total": 3})
    # fetch (roundtrip to redis not necessary but saves writing the code again)
    b64timeline = r.get("timeline.png")
    b64timeline = b64timeline.decode("utf-8")
    html = f"""<img src="data:image/png;base64, {b64timeline}" alt=" Timeline plot">"""
    return html


def clean_up_in_a_hurry():
    logger.error("Failed to execute job, timeout")


def summaryTable(df):
    df_sum = df[["release", "hostname"]].groupby("release")["hostname"].count()
    return df_sum


def dropEmptyKeys(dict):
    drop_falsey = lambda path, key, value: bool(value)
    clean = remap(dict, visit=drop_falsey)
    return clean


def makePie(df):
    plt.rcParams["text.color"] = "white"
    fig, ax = plt.subplots(figsize=(11, 9))
    fig.set_facecolor("#38373a")
    my_circle = plt.Circle((0, 0), 0.7, color="#38373a")
    df.name = ""  # remove series name
    # Pieplot + circle on it to make doughnut
    p = plt.gcf()
    p.gca().add_artist(my_circle)
    plot = df.plot.pie()
    return fig


def makeScatter(df):
    osrelease = df.release.unique()
    osrelease = sorted(osrelease)
    os_dict = dict(zip(osrelease, range(len(osrelease))))
    label = [*os_dict]

    ncolors = len(label)
    x = df["days-pending"]
    y = df["boot-time"]
    c = df.release.map(os_dict)
    plt.rcParams["text.color"] = "white"

    fig, ax = plt.subplots(figsize=(12, 8))
    pic = ax.scatter(x, y, c=c, cmap="tab20", alpha=1, clip_on=False)

    cb = plt.colorbar(pic, label="Distribution", orientation="vertical")
    cb.set_ticks(np.linspace(0, ncolors, ncolors))
    cb.set_ticklabels(label)

    ax.axvline(x=60, color="red", linestyle="-", alpha=0.7)
    ax.axvline(x=50, color="orange", linestyle="--", alpha=0.3)
    ax.axhline(y=120, color="red", linestyle="-", alpha=0.7)
    ax.axhline(y=100, color="orange", linestyle="--", alpha=0.3)
    ax.set_xlabel("Days patches pending")
    ax.set_ylabel("Days since last booted")

    # ax.set_ylim([0, 180])
    ax.set_yscale("log")
    # ax.set_xlim([0, 100])
    ax.set_xscale("log")
    return fig


def timelineGraph(df):
    """Draw graph of event label between time points on timeline"""
    color_labels = df.Project.unique()
    df["Events"] = df[["Project", "Activity"]].apply(
        lambda x: "-".join(map(str, x)), axis=1
    )
    rgb_values = sns.color_palette("Paired", len(color_labels))
    color_map = dict(zip(color_labels, rgb_values))
    labels = df["Events"]
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.autofmt_xdate()
    # axes[0] = plt.subplot2grid((6, 1), (0, 0), rowspan=5)
    color = "tab:blue"
    ax.grid(which="major", axis="x")
    ax.tick_params(axis="both", which="major", labelsize=6)
    ax.tick_params(axis="both", which="minor", labelsize=6)
    ax.set_ylabel("Project", color=color)
    ax.spines["right"].set_position(("axes", 1))
    ax.xaxis_date()
    patches = [
        plt.plot(
            [],
            [],
            marker="o",
            ms=10,
            ls="",
            mec=None,
            color=rgb_values[i],
            label="{:s}".format(color_labels[i]),
        )[0]
        for i in range(len(color_labels))
    ]
    ax.legend(handles=patches, bbox_to_anchor=(0, 1), loc="upper left")
    ax.hlines(
        df.Events,
        date2num(df.Begin),
        date2num(df.End),
        linewidth=6,
        color=df.Project.map(color_map),
        alpha=0.8,
    )
    """
    rects = ax.patches
    style = dict(size=10, color='gray')
    activity = df.Activity

    for rect, label in zip(rects, activity):
        logger.info(rect, activity)
        ax.annotate(rect.get_x(), rect.get_height(), 'wibble',
                ha='center', va='bottom', **style)
    """
    fig.tight_layout()
    return fig


def figToRdis(fig, filenamekey):
    pic_IOBytes = io.BytesIO()
    plt.savefig(pic_IOBytes, format="png")
    pic_IOBytes.seek(0)
    pic_hash = base64.b64encode(pic_IOBytes.read())
    r.set(filenamekey, pic_hash)
    return
