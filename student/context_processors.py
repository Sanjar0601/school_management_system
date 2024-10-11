def is_teacher(request):
    return {'is_teacher': getattr(request.tenant, 'is_teacher', False)}