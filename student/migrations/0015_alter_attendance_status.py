# Generated by Django 5.1.1 on 2024-12-17 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0014_auto_20241121_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('Absent', 'Absent'), ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('Yangi Yil', 'Yangi Yil')], max_length=10),
        ),
    ]