from django.shortcuts import render, redirect, get_object_or_404
from .forms import *

from .models import *
from teacher.models import PersonalInfo as Teacher
from django.views.generic import ListView
from .filters import SnippetFiler
from django.db.models import Q, Count, Prefetch
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
from django.contrib import messages
import requests
import base64
from django.conf import settings


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
            return redirect('student-registration')
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

    # Filter for students with specific statuses
    students_filter = PersonalInfo.objects.filter(status__in=['Active', 'Tekin'])

    if tenant and tenant_user:
        if tenant_user.is_teacher:
            # Teacher can only see groups where they are assigned as a teacher
            students_in_group = Group.objects.filter(
                tenant=tenant,
                teacher=tenant_user.teacher_profile,
                students__status__in=['Active', 'Tekin']
            ).prefetch_related(
                Prefetch('students', queryset=students_filter)
            ).annotate(
                group_count=Count('students', filter=Q(students__status__in=['Active', 'Tekin']))
            ).distinct()

            teachers = Teacher.objects.filter(id=tenant_user.teacher_profile.id)  # Only the teacher themselves
        else:
            # Admin can see all groups within the tenant
            students_in_group = Group.objects.filter(
                tenant=tenant
            ).prefetch_related(
                Prefetch('students', queryset=students_filter)
            ).annotate(
                group_count=Count('students', filter=Q(students__status__in=['Active', 'Tekin']))
            ).distinct()

            teachers = Teacher.objects.filter(tenant=tenant)  # Filter teachers by tenant
    else:
        # When no tenant is set, fetch all groups and teachers without tenant filtering
        students_in_group = Group.objects.filter(
            students__status__in=['Active', 'Tekin']
        ).prefetch_related(
            Prefetch('students', queryset=students_filter)
        ).annotate(
            group_count=Count('students', filter=Q(students__status__in=['Active', 'Tekin']))
        ).distinct()
        teachers = Teacher.objects.all()

    # Tenant filtering logic from GET request
    tenant_filter = request.GET.get('tenant_filter')
    if tenant_filter:
        students_in_group = Group.objects.filter(
            tenant=tenant_filter,
            students__status__in=['Active', 'Tekin']
        ).prefetch_related(
            Prefetch('students', queryset=students_filter)
        ).annotate(
            group_count=Count('students', filter=Q(students__status__in=['Active', 'Tekin']))
        ).distinct()

    tenants = Tenant.objects.all()
    days = Group.day_choices

    # Get group ID for editing students
    group_id = request.POST.get('group_id')
    edit_group_students = PersonalInfo.objects.filter(
        group=group_id, tenant=tenant, status__in=['Active', 'Tekin']
    ) if group_id else None

    context = {
        'tenants': tenants,
        'groups': students_in_group,
        'teachers': teachers,
        'days': days,
        'tenant_user': tenant_user,
        'edit_students': edit_group_students,
    }

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
        tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()

        # Fetch tenant from the request
        if tenant:
            print("Tenant found")
            qs = PersonalInfo.objects.filter(tenant=tenant)  # Filter by tenant
            if tenant_user and tenant_user.teacher_profile:
                print('User is a teacher')
                qs = qs.filter(teacher=tenant_user.teacher_profile)
            else:
                qs = PersonalInfo.objects.filter(tenant=tenant)
            group = Group.objects.filter(tenant=tenant)  # Filter groups by tenant
        else:
            print('No tenant')
            qs = PersonalInfo.objects.all()  # Fetch all records when no tenant
            group = Group.objects.all()  # Fetch all groups when no tenant
        teachers = Teacher.objects.filter(tenant=tenant) if tenant else Teacher.objects.all()
    else:
        qs = PersonalInfo.objects.none()  # No data for unauthenticated users
        group = []
        teachers = []

    tenants = Tenant.objects.all()

    # Add filtering logic based on GET parameters
    status_choices = PersonalInfo.status_choices
    language_choices = PersonalInfo.languages
    source_choices = PersonalInfo.source_choices
    name_contains_query = request.GET.get('name_contains')
    status_contains_query = request.GET.get('status_contains')
    group_contains_query = request.GET.get('group_contains')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    balance_filter = request.GET.get('balance_filter')
    tenant_filter = request.GET.get('tenant_filter')

    if name_contains_query:
        qs = qs.filter(name__icontains=name_contains_query)
    if status_contains_query:
        qs = qs.filter(status__iexact=status_contains_query)
    if group_contains_query:
        qs = qs.filter(group__id=group_contains_query)
    if balance_filter == 'positive':
        qs = qs.filter(balance__gte=0)
    elif balance_filter == 'negative':
        qs = qs.filter(balance__lt=0)
    if tenant_filter:
        qs = qs.filter(tenant_id=tenant_filter)

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
        'tenant_user': tenant_user,
        'tenants': tenants
    }
    return render(request, 'student/student-search.html', context)


class StudentDetailView(DetailView):
    model = PersonalInfo
    template_name = "student/student-detail.html"


class GroupStudentsView(View):
    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('pk')
        students = PersonalInfo.objects.filter(group=group_id, status__in=['Active', 'Tekin']).values('id', 'name', 'first_lesson_day')
        today = datetime.today().strftime('%d.%m.%Y')
        students_list = list(students)  # Convert to list for JSON serialization
        return JsonResponse({'students': students_list, 'today_date': today})


# SMS Configuration
USERNAME = "polyglotschool"  # Replace with your username
PASSWORD = "~1!6jrd)sO?r"  # Replace with your password
API_URL = "https://send.smsxabar.uz/broker-api/send"

AUTH_STRING = f"{USERNAME}:{PASSWORD}"
ENCODED_AUTH = base64.b64encode(AUTH_STRING.encode()).decode()
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {ENCODED_AUTH}",
}

# Message templates for attendance statuses
MESSAGE_TEMPLATES = {
    "Absent": "Assalomu alaykum! Farzandingiz {name} bugungi  {group} darsga kelmadi.",
    "0": "Assalomu alaykum! Farzandingiz {name} bugungi  {group} darsga kelmadi.",
    "1": "Dear {name}, your absence was EXCUSED today in {group}.",
    "2": "Assalomu alaykum! Farzandingiz {name} bugun darsga tayyorlanib kelmadi, ko`proq e'tibor ajratishingizni so`raymiz",
    "3": "Assalomu alaykum! Farzandingizning bugungi darslardagi harakatlari qoniqarsiz, ko'proq e'tibor ajratilishini so'raymiz.",
    "4": "Assalomu alaykum! {name}ning darsdagi faol harakatlari e’tiborga olindi. Ammo yanada yaxshiroq harakat qilish maqsadga muvofiq bo’lar edi.",
    "5": "Assalomu alaykum! {name} bugungi {group} darsga to'liq tayyor kelib, dars jarayonida faol qatnashganligi va o'zlashtirish darajasi a'lo ekanligini ma'lum qilamiz.",
    }
class SaveAttendanceView(View):
    def post(self, request, *args, **kwargs):
        today_date = request.POST.get('date')
        group_id = request.POST.get('group')
        unit = request.POST.get('unit')
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
                Attendance.objects.update_or_create(
                    student=student,
                    date=today_date,
                    group=group,
                    defaults={'status': status, 'unit': unit},
                )

                # Send SMS notification
                phone_number = student.phone_no  # Assuming the model has a `phone_number` field
                if phone_number:
                    self.send_sms(student, group, status, phone_number)

        return render(request, 'student/attendance_record.html')

    def send_sms(self, student, group, status, phone_number):
        # Get the appropriate message template based on status
        message_template = MESSAGE_TEMPLATES.get(status, MESSAGE_TEMPLATES)
        message_content = message_template.format(
            name=student.name,  # Assuming PersonalInfo has a `name` field
            group=group.name,  # Assuming Group has a `name` field
            status=status,
        )

        # Prepare the SMS payload
        sms_data = {
            "messages": [
                {
                    "recipient": phone_number,
                    "message-id": f"attendance_{student.id}_{group.id}",
                    "sms": {
                        "originator": "Polyglot",
                        "ttl": 300,
                        "content": {"text": message_content},
                    },
                }
            ]
        }

        # Send the SMS
        try:
            response = requests.post(API_URL, json=sms_data, headers=HEADERS)
            if response.status_code == 200:
                print(f"SMS sent successfully to {phone_number}: {message_content}")
            else:
                print(f"Failed to send SMS to {phone_number}: {response.text}")
        except requests.RequestException as e:
            print(f"Error sending SMS to {phone_number}: {e}")




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
            attendance_data = attendance_data.filter(group_id=group_filter, student__status__in=['Active', 'Tekin'])

        if month_filter:
            month_filter = int(month_filter)
            attendance_data = attendance_data.filter(date__month=month_filter, student__status__in=['Active', 'Tekin'])

        # Check if there are any records after filtering
        if attendance_data.exists():
            data_available = True

    # Get unique students and dates only if there's data available
    students = attendance_data.values('student__name').distinct().order_by('student__name') if data_available else []
    dates = attendance_data.values_list('date', 'unit').distinct().order_by('date') if data_available else []

    # Group attendance by student and date if data is available
    attendance_by_student = defaultdict(dict)
    if data_available:
        for record in attendance_data:
            key = (record.date, record.unit)
            attendance_by_student[record.student.name][key] = record.status

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


@csrf_exempt
def edit_group_view(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group = get_object_or_404(Group, id=group_id)

        # Update the group's attributes
        group.name = request.POST.get('name')
        group.teacher_id = request.POST.get('teacher')
        group.day = request.POST.get('day')
        group.time = request.POST.get('time')
        group.save()
        students_to_remove = request.POST.getlist('remove_students')
        if students_to_remove:
            PersonalInfo.objects.filter(id__in=students_to_remove, group=group).update(group=None)


        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def balance_update(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        amount = request.POST.get("amount")

        try:
            student = PersonalInfo.objects.get(id=student_id)

            balance = Balance.objects.get(student_id=student)
            balance.auth_user = request.user  # Set the updating user
            balance.amount += int(amount)
            balance.save()
            return JsonResponse({"success": True})
        except Balance.DoesNotExist:
            student = PersonalInfo.objects.get(id=student_id)
            Balance.objects.create(student=student,
                                             amount=amount)
    return JsonResponse({"success": False, "error": "Invalid request method."})


def add_expense_view(request):
    # Get the tenant associated with the current logged-in user
    tenant = getattr(request, 'tenant', None)  # Assuming user has a related 'tenant' field or model
    user = getattr((request, 'user'))
    print(user)
    if tenant is None:
        print(messages.error(request, 'No tenant found for this user.'))

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)  # Don't save yet, as we need to assign the tenant
            expense.tenant = tenant  # Assign the tenant here
            expense.save()  # Save the expense after assigning the tenant
            messages.success(request, 'Expense added successfully!')
            return redirect('add_expense')  # Redirect back to the same page
    else:
        form = ExpenseForm()  # Initialize an empty form for GET requests
    return render(request, 'student/add_expense.html', {'form': form})

class ExpenseListView(ListView):
    model = Expense
    template_name = 'student/expense_list.html'  # Adjust the template path if necessary
    context_object_name = 'expenses'

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            queryset = Expense.objects.filter(tenant=tenant)
        else:
            queryset = Expense.objects.all()
        filtered = False

        # Get filtering criteria from GET request parameters
        category = self.request.GET.get('category')
        types = self.request.GET.get('types')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        min_amount = self.request.GET.get('min_amount')
        max_amount = self.request.GET.get('max_amount')
        # Apply filters if parameters are provided
        if category:
            queryset = queryset.filter(category=category)
            filtered = True

        if types:
            queryset = queryset.filter(types=types)
            filtered = True

        if start_date:
            start_date_parsed = parse_date(start_date)
            if start_date_parsed:
                queryset = queryset.filter(timestamp__gte=start_date_parsed)
                filtered = True

        if end_date:
            end_date_parsed = parse_date(end_date)
            if end_date_parsed:
                queryset = queryset.filter(timestamp__lte=end_date_parsed)
                filtered = True

        if min_amount:
            queryset = queryset.filter(amount_spent__gte=min_amount)
            filtered = True

        if max_amount:
            queryset = queryset.filter(amount_spent__lte=max_amount)
            filtered = True

        # Add success/failure messages based on filtering results
        if filtered:
            if queryset.exists():
                messages.success(self.request, "Filter applied successfully!")
            else:
                messages.warning(self.request, "No results found for the applied filter.")
        else:
            messages.info(self.request, "No filter applied. Showing all expenses.")

        return queryset


@csrf_exempt
def delete_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')

        # Ensure group ID is provided
        if not group_id:
            return JsonResponse({'success': False, 'error': 'Group ID is required.'}, status=400)

        try:
            # Fetch the group object and delete it
            group = get_object_or_404(Group, id=group_id)
            group.delete()
            return JsonResponse({'success': True, 'message': 'Group deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)