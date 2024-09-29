from django.db.models.signals import pre_save
from django.dispatch import receiver
from account.models import TenantUser
from student.models import PersonalInfo
import threading

@receiver(pre_save, sender=PersonalInfo)
def set_tenant(sender, instance, **kwargs):
    current_user = getattr(threading.local(), 'user', None)
    if current_user:
        try:
            tenant_user = TenantUser.objects.get(user=current_user)
            instance.tenant = tenant_user.tenant
        except TenantUser.DoesNotExist:
            instance.tenant = None  # or handle accordingly
