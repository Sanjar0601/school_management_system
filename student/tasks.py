from celery import shared_task
from .models import Balance

@shared_task
def deduct_balance():
    for i in range(0,10):
        print(f'Hello {i}')
    return 'Task complete'
