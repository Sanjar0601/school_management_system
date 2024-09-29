from django.shortcuts import render, redirect

from . import forms
from .models import PersonalInfo

# Create your views here.



def teacher_list(request):
    teacher = PersonalInfo.objects.all()
    context = {'teacher': teacher}
    return render(request, 'employee/employee-list.html', context)
