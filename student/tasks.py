from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import PersonalInfo, Balance

@shared_task
def monthly_billing():
    """
    Ежемесячный биллинг студентов с учетом даты последней оплаты.
    """
    today = timezone.now().date()
    monthly_fee = 699000  # Стоимость обучения

    # Получаем всех студентов, у которых статус "Active"
    active_students = PersonalInfo.objects.filter(status="Active")

    billed_count = 0  # Счетчик обработанных студентов

    for student in active_students:
        # Получаем последнюю транзакцию
        last_balance = student.transactions.order_by('-last_transaction_date').first()

        # Если транзакций нет, используем дату первого прихода (если есть)
        last_payment_date = last_balance.last_transaction_date.date() if last_balance else student.first_come_day

        # Если вообще нет даты последнего платежа, пропускаем студента
        if not last_payment_date:
            continue

        # Проверяем, прошло ли 30 дней с последнего списания
        if (today - last_payment_date).days >= 30:
            old_balance = student.balance if student.balance else 0
            new_balance = old_balance - monthly_fee  # Списываем деньги

            # Обновляем баланс студента
            student.balance = new_balance

            # Если баланс стал отрицательным, не меняем статус, так как нужно продолжать списывать
            student.save()

            # Записываем транзакцию в баланс
            Balance.objects.create(
                student=student,
                amount=-monthly_fee,
                transaction_type="Deduction",
                description=f"Monthly fee deducted on {today}",
            )

            billed_count += 1  # Увеличиваем счетчик

    return f"Billing completed for {billed_count} students."
