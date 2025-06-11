import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-deals-every-6-hours': {
        'task': 'deals.tasks.update_deals',
        'schedule': 21600,  # 6 часов
    },
}