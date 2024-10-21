from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils.timezone import now
from account.models import TenantUser
from student.models import PersonalInfo
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

#
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
