from django.shortcuts import render, redirect
from django.db.models import Count
from . import forms
from .models import PersonalInfo

# Create your views here.


def teacher_registration(request):
    try:
        form = forms.PersonalInfoForm(request.POST)

        if request.method == 'POST':
            form = forms.PersonalInfoForm(request.POST)

            if form.is_valid():
                personal_info = form.save(commit=False)
                personal_info.save()
                return redirect('teacher-list')

        context = {
            'form': form,
        }
        return render(request, 'teacher/teacher-registration.html', context)

    except Exception as e:
        # Log the exception and return an error message or page
        print(f"Error in teacher_registration: {e}")
        return render(request, 'error_page.html', {'error': str(e)})


def teacher_list(request):
    tenant = getattr(request, 'tenant', None)

    # Ensure tenant filtering is applied
    if tenant is not None:
        # Filter by tenant and count related groups (adjust 'groups' to the correct related field name)
        teacher = PersonalInfo.objects.filter(tenant=tenant).annotate(group_count=Count('groups'))
    else:
        teacher = PersonalInfo.objects.none()  # No results if tenant is None

    context = {'teachers': teacher}
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
