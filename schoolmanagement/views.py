from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import TenantUser
import student
import teacher
import employee
from django.contrib.auth.models import User

@login_required(login_url='login')
def home_page(request):
    total_student = student.models.PersonalInfo.objects.count()
    total_teacher = teacher.models.PersonalInfo.objects.count()
    total_employee = employee.models.PersonalInfo.objects.count()
    total_class = student.models.Group.objects.count()
    current_user = request.user
    tenant_user = current_user
    context = {
        'student': total_student,
        'teacher': total_teacher,
        'employee': total_employee,
        'total_class': total_class,
        'user': current_user,
        'tenant_user': tenant_user
    }
    return render(request, 'home.html', context)


