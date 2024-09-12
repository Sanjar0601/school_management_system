# myapp/tests.py

from django.test import TransactionTestCase
from student.models import PersonalInfo as Student
from student.tasks import deduct_student_balances
from freezegun import freeze_time


class BalanceDeductionTest(TransactionTestCase):

    def setUp(self):
        # Create some test students
        self.student1 = Student.objects.create(name="John Doe", balance=0)
        self.student2 = Student.objects.create(name="Jane Doe", balance=0)
        self.student3 = Student.objects.create(name="Alex Smith", balance=0)
        self.student4 = Student.objects.create(name="Emily Johnson", balance=0)

        print(f"current balances: {self.student1.balance}, {self.student2.balance}")

    @freeze_time("2024-09-30")
    def test_balance_deduction(self):
        # Trigger the balance deduction

        deduct_student_balances(force_deduction=True)

        # Reload the student data from the database
        self.student1.refresh_from_db()
        self.student2.refresh_from_db()
        self.student3.refresh_from_db()
        self.student4.refresh_from_db()

        print(f"Updated balances: {self.student1.balance}, {self.student2.balance}")

        # Verify the expected balance after deduction
        self.assertEqual(self.student1.balance, -100)  # Deducted 10
        self.assertEqual(self.student2.balance, -100)  # Deducted 10
        self.assertEqual(self.student3.balance, -100)  # Deducted 10, now negative
        self.assertEqual(self.student4.balance, -100)  # Already negative, deducted further
