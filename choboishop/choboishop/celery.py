import os
from celery import Celery

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'choboishop.settings')

app = Celery('choboishop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
