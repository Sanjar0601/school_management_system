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
            'teacher',
            'goal',
            'first_lesson_day',
            'first_come_day',
            'status',
            'source',
            'language',
            'test',
            'learning_duration',
            'comment'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_no': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
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



class StudentSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100, required=False)





class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']