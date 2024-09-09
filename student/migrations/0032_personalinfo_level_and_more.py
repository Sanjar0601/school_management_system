# Generated by Django 5.1.1 on 2024-09-06 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0031_alter_academicinfo_registration_no_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalinfo',
            name='level',
            field=models.CharField(blank=True, choices=[('Beginner', 'Beginner'), ('Elementary', 'Elementary'), ('Pre-Intermediate', 'Pre-Intermediate'), ('Intermediate', 'Intermediate'), ('Upper-Intermediate', 'Upper-Intermediate'), ('Advanced', 'Advanced')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=542613, unique=True),
        ),
    ]
