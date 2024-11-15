from django.contrib import admin


from .models import PersonalInfo, Attendance, Group, Balance, Expense
# Register your models here.

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'time', 'day', 'teacher', 'tenant')
    exclude = ('tenant',)

admin.site.register(PersonalInfo)
admin.site.register(Attendance)
admin.site.register(Group, GroupAdmin)

admin.site.register(Expense)
admin.site.register(Balance)
