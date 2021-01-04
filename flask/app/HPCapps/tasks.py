import redis
import zlib
import pickle
import matplotlib.pyplot as plt
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
        df_sum = summaryTable(df)
        makePie(df_sum)
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
    df_sum = df[['release', 'hostname', 'owner']].groupby('release')['owner'].count()
    return df_sum

def makePie(df):
    plot = df.plot.pie()
    pic_IOBytes = io.BytesIO()
    plt.savefig(pic_IOBytes, format='png')
    pic_IOBytes.seek(0)
    pic_hash = base64.b64encode(pic_IOBytes.read())

    r.set("pie_release.png", pic_hash)
    return    