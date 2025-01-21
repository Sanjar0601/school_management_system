from django.core.management.base import BaseCommand
from student.models import PersonalInfo  # Replace with your actual model

class Command(BaseCommand):
    help = 'Deduct a specific amount from accounts monthly'

    def handle(self, *args, **kwargs):
        # Logic for the task
        students = PersonalInfo.objects.filter(status='Active')
        for student in students:
            student.balance -= 100
            student.save()
        self.stdout.write(self.style.SUCCESS('Successfully deducted amounts from eligible status'))
