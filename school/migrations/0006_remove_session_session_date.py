# Generated by Django 4.2.2 on 2023-08-27 01:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0005_alter_enrolledpackage_registration_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='session_date',
        ),
    ]