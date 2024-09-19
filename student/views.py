from django.shortcuts import render, redirect, get_object_or_404
from academic.models import ClassRegistration
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
from django.utils import timezone

@csrf_exempt
def student_update(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        status = request.POST.get('status')
        group_id = request.POST.get('group')
        teacher_id = request.POST.get('teacher')
        balance = request.POST.get('balance')  # Get balance from POST data
        first_lesson_day = request.POST.get('first_lesson_day')  # Get first_lesson_day from POST data

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
            
        if first_lesson_day:
            student.first_lesson_day = first_lesson_day

        # Save the changes to the student record
        student.save()

        # Send success response
        return JsonResponse({'success': True})

    # Send error response for non-POST requests
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)



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
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    print("Status filter:", status_contains_query)

    if name_contains_query != '' and name_contains_query is not None:
        qs = qs.filter(name__icontains=name_contains_query)
    if status_contains_query != '' and status_contains_query is not None:
        print("Valid status choices:", [status[0] for status in status_choices])
        qs = qs.filter(status__iexact=status_contains_query)
        print("Filtered QuerySet:", qs)
    if group_contains_query != '' and group_contains_query is not None:
        qs = qs.filter(group__id=group_contains_query)

    def convert_date(date_str):
        return datetime.strptime(date_str, '%d-%m-%Y').date()

    # Filter by date
    if start_date:
        try:
            start_date = convert_date(start_date)
            qs = qs.filter(first_lesson_day__gte=start_date)
        except ValueError:
            # Handle invalid date format
            pass
    if end_date:
        try:
            end_date = convert_date(end_date)
            qs = qs.filter(first_lesson_day__lte=end_date)
        except ValueError:
            # Handle invalid date format
            pass

    if start_date and not end_date:
        qs = qs.filter(first_lesson_day=start_date)
    elif end_date and not start_date:
        qs = qs.filter(first_lesson_day=end_date)
    elif start_date and end_date:
        qs = qs.filter(first_lesson_day__range=[start_date, end_date])


    context = {
        'queryset': qs, 'groups': group, 'statuses': status_choices, 'teachers': teachers
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
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=today_date,
                    status=status,
                    group=group# Include group_name if needed
                )

                if not created:  # If attendance record already exists, update it
                    attendance.status = status
                    attendance.save()

        return JsonResponse({'message': 'Attendance recorded successfully.'})

class AttendanceReportView(ListView):
    model = Attendance
    template_name = "student/attendance_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendance_records = Attendance.objects.all()

        # Get unique dates
        unique_dates = sorted(set(record.date for record in attendance_records))
        context['unique_dates'] = unique_dates

        # Structure data for easy display
        attendance_data = defaultdict(lambda: {date: '' for date in unique_dates})
        for record in attendance_records:
            attendance_data[record.student][record.date] = record.status
        context['attendance_data'] = attendance_data

        context['today'] = timezone.now().date()  # Add today's date to context

        return context

