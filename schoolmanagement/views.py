from account.models import TenantUser
from student.models import PersonalInfo
from teacher.models import PersonalInfo as Teacher
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from employee.models import PersonalInfo as Employee
from student.models import Group


@login_required(login_url='login')
def home_page(request):
    # Get the tenant and current user
    current_user = request.user
    tenant = getattr(request, 'tenant', None)

    # Initialize variables to avoid undefined errors
    total_teacher = 0
    total_class = 0

    # Count employees and classes, filtered by tenant if necessary
    total_employee = Employee.objects.count()
    tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()

    if tenant:  # Ensure there is a tenant
        queryset = PersonalInfo.objects.filter(tenant=tenant).annotate()
        # If the user is a teacher, count students assigned to them and groups they teach
        if tenant_user and tenant_user.teacher_profile:
            total_student = queryset.filter(teacher=tenant_user.teacher_profile, status__in=['Active', 'Free']).count()
            total_class = Group.objects.filter(tenant=tenant, teacher=tenant_user.teacher_profile).count()
        else:
            # Otherwise, count all students and teachers in the tenant
            total_student = queryset.filter(status__in=['Active', 'Free']).count()
            total_teacher = Teacher.objects.filter(tenant=tenant).count()
            total_class = Group.objects.filter(tenant=tenant).count()
    else:
        queryset = PersonalInfo.objects.all()
        total_student = queryset.count()
        total_teacher = Teacher.objects.all().count()
        total_class = Group.objects.all().count()

    # Pass the counts to the context
    context = {
        'student': total_student,
        'teacher': total_teacher,
        'total_class': total_class,
        'user': current_user,
        'tenant_user': tenant_user,
    }

    return render(request, 'home.html', context)