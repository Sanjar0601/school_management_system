# Generated by Django 4.2 on 2024-09-04 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0026_alter_academicinfo_registration_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=87122, unique=True),
        ),
    ]
