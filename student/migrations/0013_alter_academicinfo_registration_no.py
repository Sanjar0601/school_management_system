# Generated by Django 5.1 on 2024-08-27 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0012_auto_20200419_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicinfo',
            name='registration_no',
            field=models.IntegerField(default=199456, unique=True),
        ),
    ]
