import redis
import zlib
import pickle
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np
import base64
import io
import seaborn as sns

from celery import Celery
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

# Application imposts
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
    os_dict = dict(zip(osrelease, range(len(osrelease))))
    label = [*os_dict]
    label = sorted(label)

    ncolors = len(label)
    x = df["days-pending"]
    y = df["boot-time"]
    c = df.release.map(os_dict)
    plt.rcParams["text.color"] = "white"

    fig, ax = plt.subplots(figsize=(12, 8))
    pic = ax.scatter(x, y, c=c, cmap="tab20c", alpha=1)

    cb = plt.colorbar(pic, label="Distribution", orientation="vertical")
    cb.set_ticks(np.linspace(0, ncolors, ncolors))
    cb.set_ticklabels(label)

    ax.axvline(x=60, color="red", linestyle="-", alpha=0.7)
    ax.axvline(x=50, color="orange", linestyle="--", alpha=0.3)
    ax.axhline(y=60, color="red", linestyle="-", alpha=0.7)
    ax.axhline(y=50, color="orange", linestyle="--", alpha=0.3)
    ax.set_xlabel("Days patches pending")
    ax.set_ylabel("Days since last booted")

    ax.set_ylim([0, 180])
    ax.set_xlim([0, 100])
    return fig


def timelineGraph(df):
    """Draw graph of event label between time points on timeline"""
    color_labels = df.Project.unique()
    rgb_values = sns.color_palette("Paired", len(color_labels))
    color_map = dict(zip(color_labels, rgb_values))
    labels = df["Activity"]
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(16, 10))
    fig.autofmt_xdate()
    axes[0] = plt.subplot2grid((6, 1), (0, 0), rowspan=5)
    color = "tab:blue"
    axes[0].grid(which="major", axis="x")
    axes[0].tick_params(axis="both", which="major", labelsize=6)
    axes[0].tick_params(axis="both", which="minor", labelsize=6)
    axes[0].set_ylabel("Project", color=color)
    axes[0].spines["right"].set_position(("axes", 1))
    axes[0].xaxis_date()
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
    axes[0].legend(handles=patches, bbox_to_anchor=(0, 1), loc="upper left")
    axes[0].hlines(
        labels,
        date2num(df.Begin),
        date2num(df.End),
        linewidth=6,
        color=df.Project.map(color_map),
        alpha=0.8,
    )
    #axes[0].text(date2num(df.Begin), date2num(df.End), df.Activity, ha='center', va='center')
    # axes[0].plot(date2num(df_sub_ref.Date), df_sub_ref.User, "kx", linewidth=10)

    fig.tight_layout()
    # plt.show()
    return fig


def figToRdis(fig, filenamekey):
    pic_IOBytes = io.BytesIO()
    plt.savefig(pic_IOBytes, format="png")
    pic_IOBytes.seek(0)
    pic_hash = base64.b64encode(pic_IOBytes.read())
    r.set(filenamekey, pic_hash)
    return
