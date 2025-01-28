# student/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def my_tasker():
    logger.info("Task is running!")
    print("Task is running!")