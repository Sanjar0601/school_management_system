# Generated by Django 5.1.1 on 2024-11-20 21:27

from django.db import migrations

def update_status_choices(apps, schema_editor):
    MyModel = apps.get_model('student', 'PersonalInfo')

    MyModel.objects.filter(status='Paid').update(status='Active')

class Migration(migrations.Migration):

    dependencies = [
        ('student', '0013_delete_chert_attendance_unit_and_more'),
    ]

    operations = [
        migrations.RunPython(update_status_choices),
    ]
