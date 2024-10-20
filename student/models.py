from django.db import models
import random
import threading
from teacher.models import PersonalInfo as Teacher
from django.contrib.auth.models import User
from account.models import Tenant, TenantAwareManager


class Group(models.Model):
    name = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    day_choices = (
        ('T/T/S', 'T/T/S'),
        ('M/W/F', 'M/W/F'),
    )
    day = models.CharField(choices=day_choices, max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='groups')
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True)
    objects = TenantAwareManager()

    def __str__(self):
        return f'{self.name} | {self.teacher} | {self.day} | {self.time}'


class PersonalInfo(models.Model):
    name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=100)
    status_choices = (
        ('Comer', 'Comer'),
        ('Waiting', 'Waiting'),
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('First Lesson', 'First Lesson'),
        ('Wrong Number', 'Wrong Number'),
        ('Deposit', 'Deposit'),
        ('Deleted', 'Deleted'),


    )
    status = models.CharField(choices=status_choices, max_length=20, null=True)
    source_choices = (
        ('Instagram', 'Instagram'),
        ('Telegram', 'Telegram'),
        ('Friend', 'Friend'),
        ('Facebook', 'Facebook'),
        ('Flayer', 'Flayer'),
        ('Reklama', 'Reklama')
    )
    source = models.CharField(choices=source_choices, max_length=20, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, related_name='student_tenants')
    goal = models.CharField(max_length=100, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name='teacher')
    first_lesson_day = models.DateField(null=True)
    first_come_day = models.DateField(blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    balance = models.IntegerField(null=True, blank=True, default=-599000)
    comment = models.CharField(max_length=200, null=True, blank=True)
    learning_duration = models.CharField(max_length=100, null=True, blank=True)
    last_deduction = models.DateField(null=True, blank=True)
    objects = TenantAwareManager()
    test = models.CharField(max_length=100, null=True, blank=True)
    languages = (
        ('Russian', 'Russian'),
        ('English', 'English'),
        ('French', 'French'),
        ('German', 'German')
    )
    language = models.CharField(choices=languages, max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    student = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('Absent', 'Absent'),
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5')
        ]
    )

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"