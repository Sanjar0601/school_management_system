from django import forms

from .models import *
from account.models import TenantUser
from teacher.models import PersonalInfo as Teacher
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'teacher', 'time', 'day']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'time': forms.TextInput(attrs={'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)  # Capture tenant and remove from kwargs
        super().__init__(*args, **kwargs)  # Initialize the form as usual

        if self.tenant:
            self.fields['teacher'].queryset = Teacher.objects.filter(
                tenant=self.tenant,
            )

    def save(self, commit=True):
        instance = super().save(commit=False)  # Don't save to the database yet
        if self.tenant:
            instance.tenant = self.tenant  # Set the tenant before saving
        if commit:
            instance.save()  # Save the instance to the database
        return instance



class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = [
            'name',
            'phone_no',
            'status',
            'first_lesson_day',
            'first_come_day',
            'teacher',
            'group',
            'goal',
            'source',
            'language',
            'test',
            'learning_duration',
            'comment',

        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_no': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class':'form-control'}),
            'goal': forms.TextInput(attrs={'class': 'form-control'}),
            'first_lesson_day': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'first_come_day': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'test': forms.TextInput(attrs={'class': 'form-control'}),
            'learning_duration': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

    # Optional fields
    first_lesson_day = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    first_come_day = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)

        # Filter teacher queryset by tenant
        if self.tenant:
            self.fields['teacher'].queryset = Teacher.objects.filter(tenant=self.tenant)
        else:
            self.fields['teacher'].queryset = Teacher.objects.none()

        # Default to empty queryset for group
        self.fields['group'].queryset = Group.objects.none()

        # Dynamically update group queryset if teacher is provided in POST data
        if 'teacher' in self.data:
            try:
                teacher_id = int(self.data.get('teacher'))
                self.fields['group'].queryset = Group.objects.filter(teacher_id=teacher_id, tenant=self.tenant)
            except (ValueError, TypeError):
                self.fields['group'].queryset = Group.objects.none()
        elif self.instance.pk and self.instance.teacher:
            # Pre-fill groups for editing existing instance
            self.fields['group'].queryset = Group.objects.filter(teacher=self.instance.teacher, tenant=self.tenant)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Assuming tenant-based uniqueness
        if PersonalInfo.objects.filter(phone=phone, tenant=self.tenant).exists():
            raise forms.ValidationError("A student with this phone number already exists.")
        return phone


    def save(self, commit=True):
        instance = super().save(commit=False)  # Don't save to the database yet
        if self.tenant:
            instance.tenant = self.tenant  # Set the tenant before saving
        if commit:
            instance.save()  # Save the instance to the database
        return instance



class StudentSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100, required=False)





class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']


class GroupEditForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'time', 'day', 'teacher']  # fields to be edited in the modal form

    widgets = {
        'teacher': forms.Select(attrs={'class': 'form-control'}),
        'day': forms.Select(attrs={'class': 'form-control'})
    }
    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super(GroupEditForm, self).__init__(*args, **kwargs)
        if tenant:
            # Limit the teachers to those in the current tenant
            self.fields['teacher'].queryset = Teacher.objects.filter(tenant=tenant)


class AddBalanceForm(forms.Form):
    amount = forms.IntegerField(label='Amount', min_value=1)
    description = forms.CharField(label='Description', max_length=200, required=False)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount_spent', 'comment', 'category', 'types']
        widgets = {
            'amount_spent': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
