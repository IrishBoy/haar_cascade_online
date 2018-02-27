import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_handler.settings')

app = Celery('image_handler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()