from django.db import models
import random
import threading
from teacher.models import PersonalInfo as Teacher
from django.contrib.auth.models import User
from account.models import Tenant, TenantAwareManager
from django.utils import timezone

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
        return f'{self.teacher} | {self.name} | {self.day} | {self.time}'



class PersonalInfo(models.Model):
    name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=100)
    status_choices = (
        ('Comer', 'Comer'),
        ('Waiting', 'Waiting'),
        ('Active', 'Active'),
        ('Unpaid', 'Unpaid'),
        ('First Lesson', 'First Lesson'),
        ('Wrong Number', 'Wrong Number'),
        ('Deposit', 'Deposit'),
        ('Deleted', 'Deleted'),
        ('Frozen', 'Frozen'),
        ('Free', 'Free'),
        ('Duplicate', 'Duplicate'),
        ('Another Branch', 'Another Branch'),
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
    balance = models.IntegerField(null=True, blank=True, default=-699000)
    comment = models.CharField(max_length=200, null=True, blank=True)
    learning_duration = models.CharField(max_length=100, null=True, blank=True)
    objects = TenantAwareManager()
    deleted_date = models.DateTimeField(null=True, blank=True)
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

    def save(self, *args, **kwargs):
        # Check if this is a new student
        is_new = self.pk is None

        # Retrieve the previous balance for this student if it exists
        old_balance = None
        if not is_new:
            old_instance = PersonalInfo.objects.filter(pk=self.pk).first()
            old_balance = old_instance.balance if old_instance else None

        # Set the deleted_date if the status is 'Deleted'
        if self.status == 'Deleted':
            self.deleted_date = timezone.now()

        # Save the student
        super().save(*args, **kwargs)

        # If this is a new student, create an initial balance record
        if is_new:
            Balance.objects.create(
                student=self,
                amount=self.balance or -699000,
                transaction_type='Payment',
                description='Initial balance created for the student',
            )
        # If the balance has changed, create a new balance record
        elif old_balance != self.balance:
            Balance.objects.create(
                student=self,
                amount=self.balance - (old_balance or 0),
                transaction_type='Payment' if self.balance > (old_balance or 0) else 'Deduction',
                description='Balance updated',
            )

class Balance(models.Model):
    student = models.ForeignKey('PersonalInfo', on_delete=models.CASCADE, related_name='transactions')
    last_transaction_date = models.DateTimeField(default=timezone.now)
    amount = models.IntegerField(default=-599000)
    type_choices = (
        ('Payment', 'Payment'),
        ('Deduction', 'Deduction'),
    )
    transaction_type = models.CharField(choices=type_choices, max_length=10)
    description = models.CharField(max_length=200, null=True, blank=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.student} | {self.last_transaction_date}'




class Attendance(models.Model):
    student = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(null=True, blank=True, db_index=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, db_index=True)
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
            ('5', '5'),
        ]
    )
    unit = models.CharField(max_length=200, null=True)
    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

    class Meta:
        unique_together = ('student', 'date', 'group')


class Expense(models.Model):
    balance = models.ForeignKey(Balance, related_name='expenses', null=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    comment = models.CharField(max_length=200, blank=True)  # Reason for the expense
    amount_spent = models.IntegerField()
    category = models.CharField(max_length=150, choices=[
        ('Expense', 'Expense'),
        ('Income', 'Income'),
    ], blank=True)
    types = models.CharField(max_length=150, choices=[
        ('Humo', 'Humo'),
        ('UzCard', 'UzCard'),
        ('Click', 'Click'),
        ('Perevod', 'Perevod'),
        ('Others', 'Others')
    ], blank=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.comment} - {self.amount_spent}"



