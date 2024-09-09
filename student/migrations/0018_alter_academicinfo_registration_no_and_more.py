# Generated by Django 4.2 on 2024-09-04 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0017_alter_academicinfo_registration_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=34087, unique=True),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='date_of_birth',
            field=models.CharField(max_length=10),
        ),
    ]
