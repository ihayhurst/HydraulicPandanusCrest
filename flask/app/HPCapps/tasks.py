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
    try:
        df = getPatching()
        logger.info("ending run")
        html = applyTableStyle(df)
    except SoftTimeLimitExceeded:
        clean_up_in_a_hurry()
    return html


@celery.task(bind=True, hard_time_limit=6)
def getQueuedInventory(self):
    logger.info(self.request.id)
    html = "<h3> Your task young Padowan; failed it has</h3>"
    try:
        df = getInventory()
    except SoftTimeLimitExceeded:
        clean_up_in_a_hurry()
    html = applyInventoryStyle(df)
    html = html.set_table_attributes('class="fixedhead"').render()
    return html

def clean_up_in_a_hurry():
    logger.error('Failed to execute job, timeout')

