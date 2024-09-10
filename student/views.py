from django.shortcuts import render, redirect
from academic.models import ClassRegistration
from .forms import *
from .models import *
from teacher.models import PersonalInfo as Teacher
from django.views.generic import ListView
from .filters import SnippetFiler
from django.db.models import Q, Count
from django.views.generic import DetailView, UpdateView
from django.http import JsonResponse


from django.http import JsonResponse
from .models import PersonalInfo

def student_update(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        status = request.POST.get('status')
        group_id = request.POST.get('group')
        teacher_id = request.POST.get('teacher')

        try:
            student = PersonalInfo.objects.get(id=student_id)
            student.status = status
            student.group_id = group_id
            student.teacher_id = teacher_id
            student.save()
            return JsonResponse({'success': True})
        except PersonalInfo.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})




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
    group = Group.objects.all()
    teachers = Teacher.objects.all()
    status_choices = PersonalInfo.status_choices
    name_contains_query = request.GET.get('name_contains')
    status_contains_query = request.GET.get('status_contains')
    group_contains_query = request.GET.get('group_contains')
    print("Status filter:", status_contains_query)

    if name_contains_query != '' and name_contains_query is not None:
        qs = qs.filter(name__icontains=name_contains_query)
    elif status_contains_query != '' and status_contains_query is not None:
        print("Valid status choices:", [status[0] for status in status_choices])
        qs = qs.filter(status__iexact=status_contains_query)
        print("Filtered QuerySet:", qs)
    elif group_contains_query != '' and group_contains_query is not None:
        qs = qs.filter(group__icontains=group_contains_query)
      # Print the queryset

    context = {
        'queryset': qs, 'groups': group, 'statuses': status_choices, 'teachers': teachers
    }
    return render(request, 'student/student-search.html', context)



class StudentDetailView(DetailView):
    model = PersonalInfo
    template_name = "student/student-detail.html"