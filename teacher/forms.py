from django import forms
from . import models

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = models.PersonalInfo
        exclude = {'address', 'education', 'is_delete', 'tenant'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control'}),
            'phone_no': forms.NumberInput(attrs={'class': 'form-control'}),

        }

