# Generated by Django 5.1.1 on 2024-09-11 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0040_alter_personalinfo_balance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=750736, unique=True),
        ),
    ]