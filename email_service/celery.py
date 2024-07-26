from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_service.settings')

# Replace 'your_project' with your project's name.
app = Celery('email_service')

app.conf.enable_utc = False
app.conf.result_backend = 'django-db'  # Using Django ORM as result backend
app.conf.accept_content = ['application/json']
app.conf.result_serializer = 'json'
app.conf.task_serializer = 'json'
app.conf.cache_backend = 'default'

app.conf.update(timezone='Africa/Dar_es_Salaam')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# Configure Celery using settings from Django settings.py.
app.config_from_object(settings, namespace='CELERY')

# Celery Beat settings
app.conf.beat_schedule = {
    'say-hello-every-day-at-8': {
        'task': 'emails_app.tasks.say_helo',
        'schedule': crontab(hour=21, minute=47),
        # 'args': (2)
    }
}

# Load tasks from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
