from django import forms
from .models import PersonalInfo

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        exclude = {'address', 'education', 'is_delete', 'tenant'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control'}),
            'phone_no': forms.NumberInput(attrs={'class': 'form-control'}),

        }
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super(PersonalInfoForm, self).__init__(*args, **kwargs)


    def save(self, commit=True):
        instance = super().save(commit=False)  # Don't save to the database yet
        if self.tenant:
            instance.tenant = self.tenant  # Set the tenant before saving
        if commit:
            instance.save()  # Save the instance to the database
        return instance
