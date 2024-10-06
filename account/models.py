from teacher.models import PersonalInfo
from django.db import models
from django.contrib.auth.models import User
import threading


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TenantUser(models.Model):
    tenant = models.ForeignKey('account.Tenant', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('teacher', 'Teacher')])
    is_teacher = models.BooleanField(default=False)
    teacher_profile = models.OneToOneField('teacher.PersonalInfo', on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers')
    class Meta:
        unique_together = ('tenant', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.tenant.name} ({self.role})"


    @property
    def is_admin(self):
        return not self.is_teacher


class TenantAwareManager(models.Manager):
    def get_queryset(self):
        current_tenant = getattr(threading.local(), 'tenant', None)
        if current_tenant:
            return super().get_queryset().filter(tenant=current_tenant)
        return super().get_queryset()



