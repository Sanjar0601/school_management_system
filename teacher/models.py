from django.db import models
from academic.models import Department
from administration.models import Designation
from address.models import District, Upazilla, Union




class EducationInfo(models.Model):
    institute = models.CharField(max_length=255)
    group = models.CharField(max_length=100)
    grade = models.CharField(max_length=45)
    board = models.CharField(max_length=45)
    passing_year = models.IntegerField()

    def __str__(self):
        return self.name_of_exam




class PersonalInfo(models.Model):
    name = models.CharField(max_length=45)
    phone_no = models.CharField(max_length=11, unique=True)
    email = models.CharField(max_length=255, unique=True)
    education = models.ForeignKey(EducationInfo, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
