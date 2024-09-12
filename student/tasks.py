# myapp/tasks.py

from celery import shared_task
from datetime import date, timedelta
from django.utils.timezone import now
from student.models import PersonalInfo as Student
from celery.schedules import crontab
from django_celery_beat.models import PeriodicTask, CrontabSchedule

@shared_task
def deduct_student_balances(force_deduction=False):
    today = date.today()
    last_day_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    # Only proceed if it's the last day of the month
    if today == last_day_of_month or force_deduction:
        students = Student.objects.all()
        for student in students:
            if student.last_deduction != today:
                amount_to_deduct = 100
                student.balance -= amount_to_deduct
                student.last_deduction = today
                student.save()


deduct_student_balances()

@shared_task
def schedule_monthly_deduction():
    # Schedule to run at the last day of the month at 23:59
    schedule, created = CrontabSchedule.objects.get_or_create(
        minute='59', hour='23', day_of_month='28-31', month_of_year='*',
        day_of_week='*'
    )
    PeriodicTask.objects.create(
        crontab=schedule,
        name='Deduct Student Balances',
        task='student.tasks.deduct_student_balances',
        description='Deducts student balances at the end of the month'
    )
