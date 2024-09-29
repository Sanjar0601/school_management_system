from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(PersonalInfo)
admin.site.register(Attendance)
admin.site.register(Group)