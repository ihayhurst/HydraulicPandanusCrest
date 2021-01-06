import redis
import zlib
import pickle
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

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
EXPIRATION_SECONDS = 600


redis_url='redis://:redis:6379/0'
r = redis.StrictRedis(host='redis', port=6379, db=0)
# Initialize Celery
celery = Celery(
    'worker',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)
celery.conf.accept_content = ['json', 'msgpack', 'pickle']
celery.conf.result_serializer = 'pickle'
logger = get_task_logger(__name__)


def get_job(job_id):
    '''
    To be called from our web app.
    The job ID is passed and the celery job is returned.
    '''
    return AsyncResult(job_id, app=celery)


@celery.task(bind=True, hard_time_limit=6)
def getQueuedPatching(self):
    logger.info(self.request.id)
    logger.info("startung run")
    html = "<h3> Your task young Padowan; failed it has</h3>"
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
    html = "<h3> Your task young Padowan; failed it has</h3>"
    df = None
    try:
        df = getInventory()
    except SoftTimeLimitExceeded:
        clean_up_in_a_hurry()
    html = applyInventoryStyle(df)
    html = html.set_table_attributes('class="fixedhead"').render()
    return html

def clean_up_in_a_hurry():
    logger.error('Failed to execute job, timeout')

def summaryTable(df):
    df_sum = df[['release', 'hostname']].groupby('release')['hostname'].count()
    return df_sum

def makePie(df):
    plt.rcParams['text.color'] = 'white'
    fig, ax = plt.subplots(figsize=(11,9))
    fig.set_facecolor('#38373a')
    my_circle=plt.Circle( (0,0), 0.7, color='#38373a')
    df.name=''  #remove series name
    # Pieplot + circle on it to make doughnut
    p=plt.gcf()
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
    pic = ax.scatter(x, y, c=c, cmap="jet", alpha=1)

    cb = plt.colorbar(pic, label="Distribution", orientation="vertical")
    cb.set_ticks(np.linspace(0, ncolors, ncolors))
    cb.set_ticklabels(label)

    ax.axvline(x=60, color="red", linestyle="-", alpha=0.7)
    ax.axvline(x=50, color="orange", linestyle="--", alpha=0.3)
    ax.axhline(y=60, color="red", linestyle="-", alpha=0.7)
    ax.axhline(y=50, color="orange", linestyle="--", alpha=0.3)
    ax.set_xlabel("Days patches pending")
    ax.set_ylabel("Days since last booted")

    ax.set_ylim([0, 100])
    ax.set_xlim([0, 100])
    return fig


def figToRdis(fig, filenamekey):
    pic_IOBytes = io.BytesIO()
    plt.savefig(pic_IOBytes, format='png')
    pic_IOBytes.seek(0)
    pic_hash = base64.b64encode(pic_IOBytes.read())
    r.set(filenamekey, pic_hash)
    return