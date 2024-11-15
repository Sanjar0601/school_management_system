from django.shortcuts import render, redirect
from django.db.models import Count
from . import forms
from .models import PersonalInfo
from account.models import TenantUser, Tenant
# Create your views here.


def teacher_registration(request):
    tenant = getattr(request, 'tenant', None)
    form = forms.PersonalInfoForm(request.POST or None, request.FILES or None, tenant=tenant)
    if request.method == 'POST':
        form = forms.PersonalInfoForm(request.POST, request.FILES, tenant=tenant)
        if form.is_valid() :
            personal_info = form.save(commit=False)
            personal_info.save()
            return redirect('teacher-list')

    context = {
        'form': form,
        }
    return render(request, 'teacher/teacher-registration.html', context)


def teacher_list(request):
    tenant = getattr(request, 'tenant', None)

    # Base queryset for teachers
    if tenant is not None:
        # Filter by tenant and count related groups
        teachers = PersonalInfo.objects.filter(tenant=tenant).annotate(group_count=Count('groups'))
    else:
        teachers = PersonalInfo.objects.all().annotate(group_count=Count('groups'))

    # Get all tenants for the filter dropdown
    tenants = Tenant.objects.all()

    # Apply tenant_filter if provided in GET request
    tenant_filter = request.GET.get('tenant_filter')
    if tenant_filter:
        teachers = teachers.filter(tenant_id=tenant_filter)

    # Context data for rendering the template
    context = {
        'teachers': teachers,
        'tenants': tenants,
    }
    return render(request, 'teacher/teacher-list.html', context)

def teacher_profile(request, teacher_id):
    teacher = PersonalInfo.objects.get(id=teacher_id)
    context = {
        'teacher': teacher
    }
    return render(request, 'teacher/teacher-profile.html', context)

def teacher_delete(request, teacher_id):
    teacher = PersonalInfo.objects.get(id=teacher_id)
    teacher.is_delete = True
    teacher.save()
    return redirect('teacher-list')


def teacher_edit(request, teacher_id):
    teacher = PersonalInfo.objects.get(id=teacher_id)
    form = forms.PersonalInfoForm(instance=teacher)
    if request.method == 'POST':
        form = forms.PersonalInfoForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            personal_info = form.save(commit=False)
            personal_info.save()
            return redirect('teacher-list')
    context = {
        'form': form,
         }
    return render(request, 'teacher/teacher-edit.html', context)
