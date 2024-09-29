# Generated by Django 5.1.1 on 2024-09-29 12:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('phone_no', models.CharField(max_length=11, unique=True)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('tenant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tenants', to='account.tenant')),
            ],
        ),
    ]
