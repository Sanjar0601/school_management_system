from django.shortcuts import render, redirect
from academic.models import ClassRegistration
from .forms import *
from .models import *
from django.views.generic import ListView
from .filters import SnippetFiler
from django.db.models import Q, Count
from django.views.generic import DetailView, UpdateView

def load_upazilla(request):
    district_id = request.GET.get('district')
    upazilla = Upazilla.objects.filter(district_id=district_id).order_by('name')

    upazilla_id = request.GET.get('upazilla')
    union = Union.objects.filter(upazilla_id=upazilla_id).order_by('name')
    context = {
        'upazilla': upazilla,
        'union': union
    }
    return render(request, 'others/upazilla_dropdown_list_options.html', context)


def class_wise_student_registration(request):
    register_class = ClassRegistration.objects.all()
    context = {'register_class': register_class}
    return render(request, 'student/class-wise-student-registration.html', context)

def student_registration(request):
    personal_info_form = PersonalInfoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if personal_info_form.is_valid():
            personal_info_form.save()
            return redirect('student-list')
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
    print(f'This is function {student}')
    context = {'student': student}

    return render(request, 'student/student-list.html', context)

def student_profile(request, reg_no):
    student = AcademicInfo.objects.get(registration_no=reg_no)
    context = {
        'student': student
    }
    return render(request, 'student/student-profile.html', context)


def student_delete(request, reg_no):
    student = AcademicInfo.objects.get(registration_no=reg_no)
    student.is_delete = True
    student.save()
    return redirect('student-list')

def student_search(request):
    query = ''
    results = []
    form = StudentSearchForm(request.GET or None)

    if 'query' in request.GET:
        form = StudentSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = PersonalInfo.objects.filter( Q(name__icontains=query) |
                                                   Q(phone_no__icontains=query) |
                                                   Q(status__icontains=query))
        else:
            form = StudentSearchForm()
        return render(request, 'student/student-search.html', {'form': form,
                                                         'query': query,
                                                         'results': results} )


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

# class SearchView(ListView):
#     model = PersonalInfo
#     template_name = 'student/student-search.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data()
#         context['filter'] = SnippetFiler(self.request.GET, queryset=self.get_queryset())
#         return context

def enrolled_student(request):
    forms = EnrolledStudentForm()
    cls = request.GET.get('class_name', None)
    student = AcademicInfo.objects.filter(class_info=cls, status='not enroll')
    context = {
        'forms': forms,
        'student': student
    }
    return render(request, 'student/enrolled.html', context)

def student_enrolled(request, reg):
    student = AcademicInfo.objects.get(registration_no=reg)
    forms = StudentEnrollForm()
    if request.method == 'POST':
        forms = StudentEnrollForm(request.POST)
        if forms.is_valid():
            roll = forms.cleaned_data['roll_no']
            class_name = forms.cleaned_data['class_name']
            EnrolledStudent.objects.create(class_name=class_name, student=student, roll=roll)
            student.status = 'enrolled'
            student.save()
            return redirect('enrolled-student-list')
    context = {
        'student': student,
        'forms': forms
    }
    return render(request, 'student/student-enrolled.html', context)

def enrolled_student_list(request):
    student = EnrolledStudent.objects.all()
    forms = SearchEnrolledStudentForm()
    class_name = request.GET.get('reg_class', None)
    roll = request.GET.get('roll_no', None)
    if class_name:
        student = EnrolledStudent.objects.filter(class_name=class_name)
        context = {
            'forms': forms,
            'student': student
        }
        return render(request, 'student/enrolled-student-list.html', context)
    context = {
        'forms': forms,
        'student': student
    }
    return render(request, 'student/enrolled-student-list.html', context)


class StudentDetailView(DetailView):
    model = PersonalInfo
    template_name = "student/student-detail.html"