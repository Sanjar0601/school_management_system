# Generated by Django 4.2 on 2024-09-04 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0016_alter_academicinfo_registration_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=971351, unique=True),
        ),
    ]
