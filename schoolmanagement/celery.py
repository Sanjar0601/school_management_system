import os
from celery import Celery
from celery.schedules import crontab
from celery.schedules import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolmanagement.settings')

app = Celery('schoolmanagement')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Optional: Define a debug task for testing purposes
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Importing your tasks if you have any defined in other modules
# Example:
# from your_app.tasks import *  # You can import specific tasks or modules as needed

# (Optional) You can define periodic tasks in the Celery beat schedule if required.
# For example, to automatically deduct balances every month:
app.conf.beat_schedule = {
    'deduct-balance-every-10-seconds': {
        'task': 'student.tasks.deduct_balance',
        'schedule': timedelta(seconds=10),
    },
}

app.autodiscover_tasks()
