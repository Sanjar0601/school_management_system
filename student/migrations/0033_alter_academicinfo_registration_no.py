# Generated by Django 5.1.1 on 2024-09-07 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0032_personalinfo_level_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=252885, unique=True),
        ),
    ]
