# Generated by Django 5.1.1 on 2024-09-09 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0036_alter_academicinfo_registration_no_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalinfo',
            name='comment',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=449466, unique=True),
        ),
    ]