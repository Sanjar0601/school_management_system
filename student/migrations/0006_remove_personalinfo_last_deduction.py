# Generated by Django 5.1.1 on 2024-11-03 20:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0005_rename_transaction_date_balance_last_transaction_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personalinfo',
            name='last_deduction',
        ),
    ]
