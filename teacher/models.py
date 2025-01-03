from django.db import models
from administration.models import Designation


class PersonalInfo(models.Model):
    name = models.CharField(max_length=45, )
    phone_no = models.CharField(max_length=11, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey('account.Tenant', on_delete=models.SET_NULL, null=True, related_name='tenants')

    def __str__(self):
        return f'{self.name}  |  {self.tenant}'


