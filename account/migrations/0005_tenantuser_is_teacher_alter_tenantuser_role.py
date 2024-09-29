# Generated by Django 5.1.1 on 2024-09-29 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_remove_tenantuser_is_teacher_tenantuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantuser',
            name='is_teacher',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tenantuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('teacher', 'Teacher')], default=False, max_length=50),
            preserve_default=False,
        ),
    ]