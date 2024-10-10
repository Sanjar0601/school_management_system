def is_teacher(request):
    return {'is_teacher': getattr(request.user, 'is_teacher', False)}