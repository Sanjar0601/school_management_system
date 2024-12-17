# Generated by Django 5.1.1 on 2024-11-03 13:19

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='day',
            field=models.CharField(choices=[('T/T/S', 'T/T/S'), ('M/W/F', 'M/W/F')], max_length=100),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='language',
            field=models.CharField(blank=True, choices=[('Russian', 'Russian'), ('English', 'English'), ('French', 'French'), ('German', 'German')], max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='source',
            field=models.CharField(blank=True, choices=[('Instagram', 'Instagram'), ('Telegram', 'Telegram'), ('Friend', 'Friend'), ('Facebook', 'Facebook'), ('Flayer', 'Flayer'), ('Reklama', 'Reklama')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='personalinfo',
            name='status',
            field=models.CharField(choices=[('Comer', 'Comer'), ('Waiting', 'Waiting'), ('Paid', 'Paid'), ('Unpaid', 'Unpaid'), ('First Lesson', 'First Lesson'), ('Wrong Number', 'Wrong Number'), ('Deposit', 'Deposit'), ('Deleted', 'Deleted')], max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_date', models.DateField(default=django.utils.timezone.now)),
                ('amount', models.IntegerField()),
                ('transaction_type', models.CharField(choices=[('Payment', 'Payment'), ('Deduction', 'Deduction')], max_length=10)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='student.personalinfo')),
            ],
        ),
    ]