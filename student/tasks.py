from celery import shared_task
from django.utils.timezone import now, timedelta
from student.models import PersonalInfo, Balance

@shared_task
def deduct_student_balance():
    deduction_amount = 100000  # Example deduction amount
    current_time = now()

    # Fetch all active students
    students = PersonalInfo.objects.filter(status='Active')

    for student in students:
        # Fetch the most recent transaction for the student
        last_transaction = Balance.objects.filter(student=student).order_by('-last_transaction_date').first()

        # If no transaction exists or the last transaction was more than 30 seconds ago
        if not last_transaction or (current_time - last_transaction.last_transaction_date) >= timedelta(seconds=30):
            # Create a new deduction transaction
            transaction = Balance.objects.create(
                student=student,
                amount=-deduction_amount,
                transaction_type='Deduction',
                description='30-second deduction'
            )
            # Update the student's balance
            student.update_balance()

    return "Processed balance deductions every 30 seconds."
