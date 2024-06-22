from __future__ import absolute_import, unicode_literals
import os
from celery.schedules import crontab
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hw_tracker.settings')

app = Celery('hw_tracker')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'minus-at-midnight': {
        'task': 'tracker.tasks.move_deez',
        'schedule': crontab(minute='0', hour='0') ,  # crontab(minute='0', hour='0') every day at midnight
    },
    'send-reminder-emails': {
        'task': 'tracker.tasks.send_track_email',
        'schedule': 10.00 ,#crontab(minute='0', hour='8')  # every day at 8 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
