from django.shortcuts import render, redirect
from academic.models import ClassRegistration
from .forms import *
from .models import *
from django.views.generic import ListView
from .filters import SnippetFiler
from django.db.models import Q, Count
from django.views.generic import DetailView, UpdateView



def student_registration(request):
    personal_info_form = PersonalInfoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if personal_info_form.is_valid():
            personal_info_form.save()
            return redirect('student-search')
    context = {
         'personal_info_form': personal_info_form,
         }
    return render(request, 'student/student-registration.html', context)


def group_registration(request):
    group_reg_form = GroupForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if group_reg_form.is_valid():
            group_reg_form.save()
            return redirect('group-list')
    context = {
        'group_form': group_reg_form,
        }
    return render(request, 'student/group_form.html', context)


def group_list(request):
    groups = Group.objects.all()
    students_in_group = Group.objects.annotate(group_count=Count('students'))
    context = {'groups': students_in_group}
    return render(request, 'student/group-list.html', context)


def student_list(request):
    student = PersonalInfo.objects.all()


    context = {'student': student,  }

    return render(request, 'student/student-search.html', context)





"This is a filter function"
def BootStrapFilterView(request):
    qs = PersonalInfo.objects.all()
    name_contains_query = request.GET.get('name_contains')
    status_contains_query = request.GET.get('status_contains')
    level_contains_query = request.GET.get('level_contains')

    if name_contains_query != '' and name_contains_query is not None:
        qs = qs.filter(name__icontains=name_contains_query)
    elif status_contains_query != '' and status_contains_query is not None:
        qs = qs.filter(status__icontains=status_contains_query)
    elif level_contains_query != '' and level_contains_query is not None:
        qs = qs.filter(level__icontains=level_contains_query)

    context = {
        'queryset': qs
    }
    return render(request, 'student/student-search.html', context)



class StudentDetailView(DetailView):
    model = PersonalInfo
    template_name = "student/student-detail.html"