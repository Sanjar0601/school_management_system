from django.db import models
import random

from academic.models import ClassInfo, ClassRegistration
from address.models import District, Upazilla, Union
from teacher.models import PersonalInfo as Teacher
class Group(models.Model):
    name = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    day_choices = (
        ('EVEN', 'EVEN'),
        ('ODD', 'ODD')
    )
    day = models.CharField(choices=day_choices, max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='groups')

    def __str__(self):
        return self.name




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
        ('Deposit', 'Deposit')

    )
    status = models.CharField(choices=status_choices, max_length=20, null=True)
    source_choices = (
        ('Instagram', 'Instagram'),
        ('Telegram', 'Telegram'),
        ('Friend', 'Friend'),
        ('Facebook', 'Facebook')
    )
    source = models.CharField(choices=source_choices, max_length=20, null=True)
    goal = models.CharField(max_length=100, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    first_lesson_day = models.DateField(blank=True, null=True)
    first_come_day = models.DateField(blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    balance = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=200, null=True)
    learning_duration = models.CharField(max_length=100, null=True)
    last_deduction = models.DateField(null=True, blank=True)
    test = models.CharField(max_length=100)
    languages = (
        ('Russian', 'Russian'),
        ('English', 'English'),
        ('French', 'French')
    )
    language = models.Charfield(choices=languages, max_length=30)
    
    def __str__(self):
        return self.name


class StudentAddressInfo(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    upazilla = models.ForeignKey(Upazilla, on_delete=models.CASCADE)
    union = models.ForeignKey(Union, on_delete=models.CASCADE)
    village = models.TextField()

    def __str__(self):
        return self.village

class GuardianInfo(models.Model):
    father_name = models.CharField(max_length=100)
    father_phone_no = models.CharField(max_length=11)
    father_occupation_choice = (
        ('Agriculture', 'Agriculture'),
        ('Banker', 'Banker'),
        ('Business', 'Business'),
        ('Doctor', 'Doctor'),
        ('Farmer', 'Farmer'),
        ('Fisherman', 'Fisherman'),
        ('Public Service', 'Public Service'),
        ('Private Service', 'Private Service'),
        ('Shopkeeper', 'Shopkeeper'),
        ('Driver', 'Driver'),
        ('Worker', 'Worker'),
        ('N/A', 'N/A'),
    )
    father_occupation = models.CharField(choices=father_occupation_choice, max_length=45)
    father_yearly_income = models.IntegerField()
    mother_name = models.CharField(max_length=100)
    mother_phone_no = models.CharField(max_length=11)
    mother_occupation_choice = (
        ('Agriculture', 'Agriculture'),
        ('Banker', 'Banker'),
        ('Business', 'Business'),
        ('Doctor', 'Doctor'),
        ('Farmer', 'Farmer'),
        ('Fisherman', 'Fisherman'),
        ('Public Service', 'Public Service'),
        ('Private Service', 'Private Service'),
        ('Shopkeeper', 'Shopkeeper'),
        ('Driver', 'Driver'),
        ('Worker', 'Worker'),
        ('N/A', 'N/A'),
    )
    mother_occupation = models.CharField(choices=mother_occupation_choice, max_length=45)
    guardian_name = models.CharField(max_length=100)
    guardian_phone_no = models.CharField(max_length=11)
    guardian_email = models.EmailField(blank=True, null=True)
    relationship_choice = (
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
    )
    relationship_with_student = models.CharField(choices=relationship_choice, max_length=45)

    def __str__(self):
        return self.guardian_name

class EmergencyContactDetails(models.Model):
    emergency_guardian_name = models.CharField(max_length=100)
    address = models.TextField()
    relationship_choice = (
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
    )
    relationship_with_student = models.CharField(choices=relationship_choice, max_length=45)
    phone_no = models.CharField(max_length=11)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.emergency_guardian_name

class PreviousAcademicInfo(models.Model):
    institute_name = models.CharField(max_length=100)
    name_of_exam = models.CharField(max_length=100)
    group = models.CharField(max_length=45)
    gpa = models.CharField(max_length=10)
    board_roll = models.IntegerField()
    passing_year = models.IntegerField()

    def __str__(self):
        return self.institute_name

class PreviousAcademicCertificate(models.Model):
    birth_certificate = models.FileField(upload_to='documents/', blank=True)
    release_letter = models.FileField(upload_to='documents/', blank=True)
    testimonial = models.FileField(upload_to='documents/', blank=True)
    marksheet = models.FileField(upload_to='documents/', blank=True)
    stipen_certificate = models.FileField(upload_to='documents/', blank=True)
    other_certificate = models.FileField(upload_to='documents/', blank=True)

class AcademicInfo(models.Model):
    class_info = models.ForeignKey(ClassInfo, on_delete=models.CASCADE)
    registration_no = models.IntegerField(unique=True, default=random.randint(000000, 999999))
    status_select = (
        ('not enroll', 'Not Enroll'),
        ('enrolled', 'Enrolled'),
        ('regular', 'Regular'),
        ('irregular', 'Irregular'),
        ('passed', 'Passed'),
    )
    status = models.CharField(choices=status_select, default='not enroll', max_length=15)
    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE, null=True)
    address_info = models.ForeignKey(StudentAddressInfo, on_delete=models.CASCADE, null=True)
    guardian_info = models.ForeignKey(GuardianInfo, on_delete=models.CASCADE, null=True)
    emergency_contact_info = models.ForeignKey(EmergencyContactDetails, on_delete=models.CASCADE, null=True)
    previous_academic_info = models.ForeignKey(PreviousAcademicInfo, on_delete=models.CASCADE, null=True)
    previous_academic_certificate = models.ForeignKey(PreviousAcademicCertificate, on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now_add=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.registration_no)

class EnrolledStudent(models.Model):
    class_name = models.ForeignKey(ClassRegistration, on_delete=models.CASCADE)
    student = models.OneToOneField(AcademicInfo, on_delete=models.CASCADE)
    roll = models.IntegerField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['class_name', 'roll']
    
    def __str__(self):
        return str(self.roll)


class Attendance(models.Model):
    student = models.ForeignKey(PersonalInfo, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
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

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"