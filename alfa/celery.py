import os
from celery import Celery
from celery.signals import task_failure, worker_process_init
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alfa.settings')

app = Celery('alfa')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

logger = logging.getLogger(__name__)

@task_failure.connect
def handle_task_failure(**kwargs):
    task = kwargs.get('sender')
    exception = kwargs.get('exception')
    logger.error(f'Task {task.name} failed: {exception}')

@worker_process_init.connect
def configure_worker(**kwargs):
    logger.info('Celery worker process initialized')

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')