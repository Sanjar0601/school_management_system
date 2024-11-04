from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from account.models import TenantUser
from student.models import PersonalInfo, Balance
import threading
import datetime

@receiver(pre_save, sender=PersonalInfo)
def set_tenant(sender, instance, **kwargs):
    current_user = getattr(threading.local(), 'user', None)
    if current_user:
        try:
            tenant_user = TenantUser.objects.get(user=current_user)
            instance.tenant = tenant_user.tenant
        except TenantUser.DoesNotExist:
            instance.tenant = None  # or handle accordingly

@receiver(post_save, sender=Balance)
@receiver(post_delete, sender=Balance)
def update_student_balance(sender, instance, **kwargs):
    student = instance.student
    total_balance = student.transactions.aggregate(total=models.Sum('amount'))['total'] or 0
    student.balance = total_balance
    student.save()

@receiver(post_save, sender=PersonalInfo)
def set_initial_balance(sender, instance, created, **kwargs):
    if created and instance.balance is None:  # Check if the student is newly created and balance is unset
        # Set the default balance by creating an initial Balance transaction
        default_amount = -599000  # Replace with your desired default value
        Balance.objects.create(
            student=instance,
            amount=default_amount,
            transaction_type='Payment',
            description='Initial balance'
        )
        # Update the balance field in PersonalInfo with the default amount
        instance.balance = default_amount
        instance.save()

# @receiver(post_save, sender=PersonalInfo)
# def deduct_balance(sender, instance, created, **kwargs):
#     if not created:
#         # Convert first_lesson_day to date if it's passed as a string
#         if isinstance(instance.first_lesson_day, str):
#             instance.first_lesson_day = datetime.datetime.strptime(instance.first_lesson_day, "%Y-%m-%d").date()
#         if instance.balance and isinstance(instance.balance, str):
#             instance.balance = int(instance.balance)
#         if instance.first_lesson_day:
#             today = now().date()
#             deduction_day = instance.first_lesson_day + timedelta(days=30)
#             if today >= deduction_day:
#                 instance.balance -= 599000
#                 PersonalInfo.objects.filter(pk=instance.pk).update(balance=instance.balance)
