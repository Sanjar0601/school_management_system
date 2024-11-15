def is_teacher(request):
    return {'is_teacher': getattr(request.tenant, 'is_teacher', False)}

# In your context_processors.py
def add_superadmin_status(request):
    tenant = getattr(request, 'tenant', None)
    is_superadmin = tenant is None
    return {'is_superadmin': is_superadmin}
