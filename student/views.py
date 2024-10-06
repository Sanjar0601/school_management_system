import threading
from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from teacher.models import PersonalInfo as Teacher
from django.views.generic import ListView
from .filters import SnippetFiler
from django.db.models import Q, Count
from django.views.generic import DetailView, CreateView
from django.views import View
from django.http import JsonResponse
from .models import PersonalInfo
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, timedelta
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date
from collections import defaultdict
from django.utils.timezone import now
from account.models import TenantUser


@csrf_exempt
def student_update(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        status = request.POST.get('status')
        group_id = request.POST.get('group')
        teacher_id = request.POST.get('teacher')
        balance = request.POST.get('balance')  # Get balance from POST data
        first_lesson_day = request.POST.get('first_lesson_day')
        source = request.POST.get('source')# Get first_lesson_day from POST data
        name = request.POST.get('name')
        comment = request.POST.get('comment')
        phone = request.POST.get('phone')
        goal = request.POST.get('goal')
        language = request.POST.get('language')
        test = request.POST.get('test')
        # Fetch the student object from the database
        student = get_object_or_404(PersonalInfo, id=student_id)

        # Update the student's status
        if status:
            student.status = status

        # Update the student's group if provided
        if group_id:
            group = get_object_or_404(Group, id=group_id)
            student.group = group

        # Update the student's teacher if provided
        if teacher_id:
            teacher = get_object_or_404(Teacher, id=teacher_id)
            student.teacher = teacher

        if balance:
            student.balance = balance

        if comment:
            student.comment = comment

        if source:
            student.source = source

        if name:
            student.name = name

        if first_lesson_day:
            student.first_lesson_day = first_lesson_day

        if phone:
            student.phone_no = phone

        if goal:
            student.goal = goal

        if language:
            student.languages = language

        if test:
            student.test = test


        # Save the changes to the student record
        student.save()

        # Send success response
        return JsonResponse({'success': True})

    # Send error response for non-POST requests
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def student_registration(request):
    tenant = getattr(request, 'tenant', None)
    personal_info_form = PersonalInfoForm(request.POST or None, request.FILES or None, tenant=tenant)
    print(tenant)
    if request.method == 'POST':
        personal_info_form = PersonalInfoForm(request.POST, tenant=tenant)
        if personal_info_form.is_valid():
            personal_info_form.save()
            return redirect('student-search')
    context = {
         'personal_info_form': personal_info_form,
         }
    return render(request, 'student/student-registration.html', context)


def group_registration(request):
    tenant = getattr(request, 'tenant', None)
    group_reg_form = GroupForm(request.POST or None, request.FILES or None, tenant=tenant)
    if request.method == 'POST':
        group_reg_form = GroupForm(request.POST, tenant=tenant)
        if group_reg_form.is_valid():
            group_reg_form.save()
            return redirect('group-list')
    context = {
        'group_form': group_reg_form,
        }
    return render(request, 'student/group_form.html', context)


def group_list(request):
    tenant = getattr(request, 'tenant', None)  # Get the current tenant

    # Get the current TenantUser (if exists)
    tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()

    if tenant and tenant_user:
        if tenant_user.is_teacher:
            # Teacher can only see groups where they are assigned as a teacher
            students_in_group = Group.objects.filter(
                tenant=tenant,
                teacher=tenant_user.teacher_profile  # Assuming Group has a ForeignKey to teacher (PersonalInfo)
            ).annotate(
                group_count=Count('students', filter=Q(students__status='Paid'))
            )
        else:
            # Admin can see all groups within the tenant
            students_in_group = Group.objects.filter(
                tenant=tenant
            ).annotate(
                group_count=Count('students', filter=Q(students__status='Paid'))
            )
    else:
        students_in_group = Group.objects.none()  # No groups if no tenant or user is not assigned properly

    context = {'groups': students_in_group}
    return render(request, 'student/group-list.html', context)


def student_list(request):
    pass
#     if request.user.is_authenticated:
#         tenant = getattr(threading.local(), 'tenant', None)
#         if tenant:
#             print(f'Current tenant: {tenant.name}')
#             student = PersonalInfo.objects.filter(tenant=tenant)
#         else:
#             data = []
#     context = {'student': student, }
#     return render(request, 'student/student-search.html', context)
#




"This is a filter function"


def BootStrapFilterView(request):
    if request.user.is_authenticated:
        tenant = getattr(request, 'tenant', None)
        # Fetch tenant from the request
        if tenant:
            print("Tenant found")
            qs = PersonalInfo.objects.filter(tenant=tenant)  # Filter by tenant
        else:
            qs = PersonalInfo.objects.none()
            print('No tenant')# No data if no tenant is found
        group = Group.objects.filter(tenant=tenant)  # Filter groups by tenant
        teachers = Teacher.objects.filter(tenant=tenant)  # Filter teachers by tenant
    else:
        qs = PersonalInfo.objects.none()  # No data for unauthenticated users
        group = []
        teachers = []
    # Add filtering logic based on GET parameters
    status_choices = PersonalInfo.status_choices
    language_choices = PersonalInfo.languages
    source_choices = PersonalInfo.source_choices
    name_contains_query = request.GET.get('name_contains')
    status_contains_query = request.GET.get('status_contains')
    group_contains_query = request.GET.get('group_contains')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if name_contains_query:
        qs = qs.filter(name__icontains=name_contains_query)
    if status_contains_query:
        qs = qs.filter(status__iexact=status_contains_query)
    if group_contains_query:
        qs = qs.filter(group__id=group_contains_query)

    def convert_date(date_str):
        return datetime.strptime(date_str, '%d-%m-%Y').date()

    # Filter by date
    if start_date:
        try:
            start_date = convert_date(start_date)
            qs = qs.filter(first_lesson_day__gte=start_date)
        except ValueError:
            pass
    if end_date:
        try:
            end_date = convert_date(end_date)
            qs = qs.filter(first_lesson_day__lte=end_date)
        except ValueError:
            pass

    if start_date and not end_date:
        qs = qs.filter(first_lesson_day=start_date)
    elif end_date and not start_date:
        qs = qs.filter(first_lesson_day=end_date)
    elif start_date and end_date:
        qs = qs.filter(first_lesson_day__range=[start_date, end_date])

    context = {
        'queryset': qs,
        'groups': group,
        'statuses': status_choices,
        'teachers': teachers,
        'sources': source_choices,
        'languages': language_choices,
    }
    return render(request, 'student/student-search.html', context)


class StudentDetailView(DetailView):
    model = PersonalInfo
    template_name = "student/student-detail.html"


class GroupStudentsView(View):
    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('pk')
        students = PersonalInfo.objects.filter(group=group_id).values('id', 'name', 'first_lesson_day')
        today = datetime.today().strftime('%d.%m.%Y')
        students_list = list(students)  # Convert to list for JSON serialization
        return JsonResponse({'students': students_list, 'today_date': today})


class SaveAttendanceView(View):
    def post(self, request, *args, **kwargs):
        today_date = request.POST.get('date')
        group_id = request.POST.get('group')
        group = get_object_or_404(Group, id=group_id)
        # Validate and parse the date
        if today_date:
            today_date = parse_date(today_date)
        else:
            return JsonResponse({'error': 'Date is required.'}, status=400)

        if not today_date:
            return JsonResponse({'error': 'Invalid date format.'}, status=400)
        for key, value in request.POST.items():
            if key.startswith('attendance_'):
                student_id = key.split('_')[1]
                status = value

                try:
                    student = PersonalInfo.objects.get(id=student_id)
                except PersonalInfo.DoesNotExist:
                    continue

                # Save or update the attendance record
                obj, created = Attendance.objects.update_or_create(
                    student=student,
                    date=today_date,
                    group=group,
                    defaults={'status':status}

                )
        return JsonResponse({'message': 'Attendance recorded successfully.'})




def attendance_table(request):
    # Get filters from GET parameters
    tenant = getattr(request, 'tenant', None)
    group_filter = request.GET.get('group')
    month_filter = request.GET.get('month')

    # Initialize attendance data and a flag to determine if data is present
    attendance_data = Attendance.objects.select_related('student', 'group')
    data_available = False

    # Apply filters if provided
    if group_filter or month_filter:
        if group_filter:
            attendance_data = attendance_data.filter(group_id=group_filter)

        if month_filter:
            month_filter = int(month_filter)
            attendance_data = attendance_data.filter(date__month=month_filter)

        # Check if there are any records after filtering
        if attendance_data.exists():
            data_available = True

    # Get unique students and dates only if there's data available
    students = attendance_data.values('student__name').distinct().order_by('student__name') if data_available else []
    dates = attendance_data.values_list('date', flat=True).distinct().order_by('date') if data_available else []

    # Group attendance by student and date if data is available
    attendance_by_student = defaultdict(dict)
    if data_available:
        for record in attendance_data:
            attendance_by_student[record.student.name][record.date] = record.status

    # Prepare context for rendering
    context = {
        'students': students,
        'dates': dates,
        'attendance_by_student': attendance_by_student,
        'groups': Group.objects.filter(tenant=tenant),
        'months': [
            {'value': 1, 'name': 'January'},
            {'value': 2, 'name': 'February'},
            {'value': 3, 'name': 'March'},
            {'value': 4, 'name': 'April'},
            {'value': 5, 'name': 'May'},
            {'value': 6, 'name': 'June'},
            {'value': 7, 'name': 'July'},
            {'value': 8, 'name': 'August'},
            {'value': 9, 'name': 'September'},
            {'value': 10, 'name': 'October'},
            {'value': 11, 'name': 'November'},
            {'value': 12, 'name': 'December'},
        ],
        'data_available': data_available,  # Flag to indicate if data is available
    }

    return render(request, 'student/attendance_list.html', context)
