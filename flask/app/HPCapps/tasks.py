from celery import Celery
from celery.result import AsyncResult

# Application imposts
from .patching_load import getPatching
from .patching_style import applyTableStyle


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


def get_job(job_id):
    '''
    To be called from our web app.
    The job ID is passed and the celery job is returned.
    '''
    return AsyncResult(job_id, app=celery)


@celery.task()
def getQueuedPatching():
    df = getPatching()
    df = applyTableStyle(df)
    return df