from django.contrib import admin


from .models import *
# Register your models here.

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'time', 'day', 'teacher', 'tenant')
    exclude = ('tenant',)

admin.site.register(PersonalInfo)
admin.site.register(Attendance)
admin.site.register(Group, GroupAdmin)
admin.site.register(Balance)
admin.site.register(Expense)