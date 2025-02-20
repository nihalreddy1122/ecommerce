import os
from celery import Celery

# Set default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_platform.settings')

app = Celery('ecommerce_platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# Namespace 'CELERY' means all Celery-related configs in settings should start with 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from installed apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
