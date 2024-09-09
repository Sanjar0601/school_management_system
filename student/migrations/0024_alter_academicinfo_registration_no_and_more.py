# Generated by Django 4.2 on 2024-09-04 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0023_alter_academicinfo_registration_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=770542, unique=True),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='first_come_day',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='first_lesson_day',
            field=models.DateField(auto_now_add=True),
        ),
    ]
