from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .message_templates import *
from .models import *
from teacher.models import PersonalInfo as Teacher
from django.views.generic import ListView
from django.db.models import Prefetch
from django.db.models import OuterRef, Subquery, Count, Q, Value, IntegerField
from django.db.models.functions import Coalesce, ExtractYear
from django.views.generic import DetailView
from django.views import View
from django.http import JsonResponse
from .models import PersonalInfo
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.urls import reverse
from django.utils.dateparse import parse_date
from collections import defaultdict
from account.models import TenantUser
from django.contrib import messages
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from urllib.parse import urlencode
import requests
import base64


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
    personal_info_form = PersonalInfoForm(request.POST or None,
                                          request.FILES or None,
                                          tenant=tenant)
    print(tenant)
    if request.method == 'POST':
        personal_info_form = PersonalInfoForm(request.POST, tenant=tenant)
        if personal_info_form.is_valid():
            personal_info_form.save()
            return redirect('student-registration')
    else:
        personal_info_form = PersonalInfoForm(tenant=tenant)
    context = {
         'personal_info_form': personal_info_form,
         }
    return render(request, 'student/student-registration.html', context)


def load_groups(request):
    teacher_id = request.GET.get('teacher_id')
    tenant = getattr(request, 'tenant', None)
    groups = Group.objects.filter(teacher=teacher_id, tenant=tenant).values('id', 'name', 'day', 'time')
    return JsonResponse(list(groups), safe=False)


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

@csrf_exempt
def delete_group(request):
    if request.method == 'GET':
        group_id = request.GET.get('group_id')
        print('Group id:',group_id)
        # Ensure group ID is provided
        if not group_id:
            return JsonResponse({'success': False, 'error': 'Group ID is required.'}, status=400)

        try:
            # Fetch the group object and delete it
            group = get_object_or_404(Group, id=group_id)
            group.delete()
            return redirect(reverse('group-list'))
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)



def group_list(request):
    tenant = getattr(request, 'tenant', None)  # Get the current tenant
    tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()  # Get the TenantUser instance
    is_superuser = request.user.is_superuser  # Check if the user is a superuser

    # Subquery to count students in each group with status 'Active' or 'Tekin'
    student_count_subquery = PersonalInfo.objects.filter(
        group=OuterRef('pk'),  # Relate to the Group model
        status__in=['Active', 'Tekin']
    )

    # Apply tenant filtering only if tenant is not None and user is not a superuser
    if tenant and not is_superuser:
        student_count_subquery = student_count_subquery.filter(tenant=tenant)

    student_count_subquery = student_count_subquery.values('group').annotate(count=Count('pk')).values('count')

    # Base queryset for groups
    students_in_group = Group.objects.annotate(
        group_count=Coalesce(Subquery(student_count_subquery, output_field=IntegerField()), Value(0))
    ).distinct()

    # Debug: Print the queryset to verify group_count
    for group in students_in_group:
        print(f"Group: {group.name}, Student Count: {group.group_count}")

    # Apply tenant-specific filtering
    if tenant and tenant_user:
        if tenant_user.is_teacher:
            # Teachers see only groups they teach
            students_in_group = students_in_group.filter(
                tenant=tenant,
                teacher=tenant_user.teacher_profile
            )
        else:
            # Admins see all groups for the tenant
            students_in_group = students_in_group.filter(tenant=tenant)
    elif not is_superuser:
        # No tenant context; fetch all groups with students in 'Active' or 'Tekin' status
        students_in_group = students_in_group.filter(students__status__in=['Active', 'Tekin'])

    # Apply additional tenant filtering from query parameters
    tenant_filter = request.GET.get('tenant_filter')
    if tenant_filter:
        students_in_group = students_in_group.filter(tenant=tenant_filter)

    # Pagination
    page = request.GET.get('page', 1)  # Get the page number from the query params
    paginator = Paginator(students_in_group, 10)  # Paginate with 10 items per page

    try:
        students_in_group = paginator.page(page)
    except PageNotAnInteger:
        students_in_group = paginator.page(1)
    except EmptyPage:
        students_in_group = paginator.page(paginator.num_pages)

    # Encode query parameters for reuse in pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')  # Remove the 'page' parameter to avoid duplication
    query_string = urlencode(query_params)

    # Other context data
    tenants = Tenant.objects.all()  # List of all tenants
    days = Group.day_choices  # Day choices for groups
    group_id = request.POST.get('group_id')  # Get group ID for editing students
    edit_group_students = (
        PersonalInfo.objects.filter(group=group_id, tenant=tenant, status__in=['Active', 'Tekin'])
        if group_id else None
    )

    context = {
        'tenants': tenants,  # List of tenants
        'groups': students_in_group,  # Paginated group data
        'teachers': Teacher.objects.filter(tenant=tenant) if tenant else Teacher.objects.all(),
        'days': days,  # Day options
        'tenant_user': tenant_user,  # Current tenant user info
        'edit_students': edit_group_students,  # Students for editing
        'query_string': query_string,  # Encoded query string for pagination
        'is_superadmin': is_superuser,  # Pass superuser status to the template
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



def convert_date(date_str):
    if not date_str:
        return None
    try:
        # Parse the date string into a naive datetime
        naive_date = datetime.strptime(date_str, '%Y-%m-%d')
        # Make it timezone-aware
        return timezone.make_aware(naive_date)
    except ValueError:
        return None



def BootStrapFilterView(request):
    if not request.user.is_authenticated:
        return render(request, 'student/student-search.html', {
            'queryset': PersonalInfo.objects.none(),
            'groups': [],
            'statuses': PersonalInfo.status_choices,
            'teachers': [],
            'sources': PersonalInfo.source_choices,
            'languages': PersonalInfo.languages,
            'tenant_user': None,
            'tenants': Tenant.objects.all(),
        })

    tenant = getattr(request, 'tenant', None)
    tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()

    # Base querysets
    personal_info_qs = (PersonalInfo.objects.filter(tenant=tenant).
                        select_related('tenant', 'teacher', 'group')) \
        if tenant else (PersonalInfo.objects.all().
                        select_related('tenant', 'teacher', 'group'))
    group_qs = Group.objects.filter(tenant=tenant).select_related('teacher', 'tenant') if tenant else Group.objects.all().select_related('teacher', 'tenant')
    teacher_qs = Teacher.objects.filter(tenant=tenant).select_related('tenant').values('name') if tenant else Teacher.objects.all().select_related('tenant')
    tenant_qs = Tenant.objects.all()

    # Adjust personal_info_qs based on the user's profile
    if tenant_user and tenant_user.teacher_profile:
        personal_info_qs = personal_info_qs.filter(teacher=tenant_user.teacher_profile)

    # Apply filters from GET parameters
    filters = {
        'name__icontains': request.GET.get('name_contains'),
        'status__iexact': request.GET.get('status_contains'),
        'group__id': request.GET.get('group_contains'),
        'tenant_id': request.GET.get('tenant_filter'),
    }
    # Remove empty filters
    filters = {key: value for key, value in filters.items() if value}
    personal_info_qs = personal_info_qs.filter(**filters)

    # Handle balance filter
    balance_filter = request.GET.get('balance_filter')
    if balance_filter == 'positive':
        personal_info_qs = personal_info_qs.filter(balance__gte=0)
    elif balance_filter == 'negative':
        personal_info_qs = personal_info_qs.filter(balance__lt=0)

    # Handle date filters
    start_date = convert_date(request.GET.get('start_date'))
    end_date = convert_date(request.GET.get('end_date'))

    # Determine which date field to filter based on the status
    status_filter = request.GET.get('status_contains')
    date_field = 'deleted_date' if status_filter == 'Deleted' else 'first_lesson_day'

    if start_date and end_date:
        personal_info_qs = personal_info_qs.filter(**{f'{date_field}__range': [start_date, end_date]})
    elif start_date:
        personal_info_qs = personal_info_qs.filter(**{f'{date_field}__gte': start_date})
    elif end_date:
        personal_info_qs = personal_info_qs.filter(**{f'{date_field}__lte': end_date})

    # Apply pagination to the filtered queryset
    paginator = Paginator(personal_info_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get the current query parameters
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']  # Remove the 'page' parameter to avoid duplication

    # Ensure start_date and end_date are included in query_params
    print(f"start_date: {start_date}, end_date: {end_date}")  # Debug print

    if 'start_date' in request.GET:
        query_params['start_date'] = request.GET['start_date']
    if 'end_date' in request.GET:
        query_params['end_date'] = request.GET['end_date']

    # Prepare context for the template
    context = {
        'page_obj': page_obj,
        'groups': group_qs,
        'statuses': PersonalInfo.status_choices,
        'teachers': teacher_qs,
        'sources': PersonalInfo.source_choices,
        'languages': PersonalInfo.languages,
        'tenant_user': tenant_user,
        'tenants': tenant_qs,
        'query_params': urlencode(query_params),  # Pass the query parameters to the template
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
                if status.strip() == " " or status == "Choice":
                    continue
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
    tenant = getattr(request, 'tenant', None)
    user = request.user

    # Get the user's TenantUser object
    tenant_user = TenantUser.objects.filter(user=user, tenant=tenant).select_related('tenant', 'user').first()

    # Handle missing TenantUser cases
    if not tenant_user:
        return render(request, 'student/attendance_list.html', {'error': 'User does not belong to a tenant'})

    group_filter = request.GET.get('group')
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')

    # Base QuerySet
    attendance_data = Attendance.objects.select_related('student', 'group', 'tenant')

    # Apply visibility rules based on user role
    if tenant_user.is_teacher:
        # Teachers can only see their own attendance data
        attendance_data = attendance_data.filter(group__teacher=tenant_user.teacher_profile)
        groups = Group.objects.filter(tenant=tenant, teacher=tenant_user.teacher_profile).prefetch_related('teacher')
    else:
        # Admins can see all attendance data for their tenant
        attendance_data = attendance_data.filter(group__tenant=tenant)
        groups = Group.objects.filter(tenant=tenant).prefetch_related('teacher')

    # Extract distinct years from the attendance records
    existing_years = (
        attendance_data.annotate(year=ExtractYear('date'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('year')
    )

    # Ensure attendance is only shown when all filters are applied
    data_available = bool(group_filter and month_filter and year_filter)

    if data_available:
        attendance_data = attendance_data.filter(
            group_id=group_filter,
            date__month=int(month_filter),
            date__year=int(year_filter)
        )

        attendance_data = attendance_data.prefetch_related(
            Prefetch('student', queryset=PersonalInfo.objects.only('name')),
            Prefetch('group', queryset=Group.objects.only('name', 'teacher__name'))
        )

    students = attendance_data.values('student__name').distinct().order_by('student__name') if data_available else []
    dates = attendance_data.values_list('date', 'unit').distinct().order_by('date') if data_available else []

    attendance_by_student = defaultdict(dict)
    if data_available:
        for record in attendance_data:
            key = (record.date, record.unit)
            attendance_by_student[record.student.name][key] = record.status

    context = {
        'students': students,
        'dates': dates,
        'attendance_by_student': attendance_by_student,
        'groups': groups,
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
        'years': existing_years,  # Use the distinct years from the records
        'data_available': data_available,  # Ensures table is only displayed when all filters are applied
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

        if not student_id or not amount:
            return JsonResponse({"success": False, "error": "Missing required fields."})

        try:
            # Get the student
            student = get_object_or_404(PersonalInfo, id=student_id)

            # Update the balance field in PersonalInfo
            student.balance = (student.balance or 0) + int(amount)
            student.save()

            return JsonResponse({"success": True, "new_balance": student.balance})

        except PersonalInfo.DoesNotExist:
            return JsonResponse({"success": False, "error": "Student does not exist."})
        except ValueError:
            return JsonResponse({"success": False, "error": "Invalid amount format."})

    return JsonResponse({"success": False, "error": "Invalid request method."})

def add_expense_view(request):
    # Get the tenant associated with the current logged-in user
    tenant = getattr(request, 'tenant', None)  # Assuming user has a related 'tenant' field or model
    tenant_user = TenantUser.objects.get(user=request.user, tenant=tenant)
    if tenant is None:
        print(messages.error(request, 'No tenant found for this user.'))

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)  # Don't save yet, as we need to assign the tenant
            expense.tenant = tenant  # Assign the tenant here
            expense.auth_user = tenant_user.user
            expense.save()  # Save the expense after assigning the tenant
            messages.success(request, 'Expense added successfully!')
            return redirect('add_expense')  # Redirect back to the same page
    else:
        form = ExpenseForm()  # Initialize an empty form for GET requests
    return render(request, 'student/add_expense.html', {'form': form})


class ExpenseListView(ListView):
    model = Expense
    template_name = 'student/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20  # Number of items per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # This adds `page_obj` to the context
        context['tenants'] = Tenant.objects.all()

        # Add query parameters to context for pagination links
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']  # Remove the 'page' parameter to avoid duplication
        context['query_params'] = query_params.urlencode()

        return context

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            queryset = (Expense.objects.filter(tenant=tenant).
                        select_related('auth_user', 'tenant').order_by('-timestamp'))
        else:
            queryset = (Expense.objects.all().
                        select_related('auth_user', 'tenant').order_by('-timestamp'))

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            queryset = (Expense.objects.filter(tenant=tenant).
                        select_related('auth_user', 'tenant').order_by('-timestamp'))
        else:
            queryset = (Expense.objects.all().
                        select_related('auth_user', 'tenant').order_by('-timestamp'))
        filtered = False

        # Get filtering criteria from GET request parameters
        category = self.request.GET.get('category')
        types = self.request.GET.get('types')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        min_amount = self.request.GET.get('min_amount')
        max_amount = self.request.GET.get('max_amount')
        branch = self.request.GET.get('branch')

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

        if branch:
            queryset = queryset.filter(tenant_id=branch)
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


def update_expense(request):
    if request.method == 'POST':
        expense_id = request.POST.get('expense_id')
        comment = request.POST.get('comment')
        category = request.POST.get('category')
        types = request.POST.get('types')
        amount_spent = request.POST.get('amount_spent')

        expense = get_object_or_404(Expense, id=expense_id)

        expense.comment = comment
        expense.category = category
        expense.types = types
        expense.amount_spent = amount_spent
        expense.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

