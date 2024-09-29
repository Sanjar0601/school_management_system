from django.contrib import admin
from .models import *
# from advanced_filters.admin import AdminAdvancedFiltersMixin

# admin.site.register(UserProfile)


admin.site.register(Tenant)
admin.site.register(TenantUser)