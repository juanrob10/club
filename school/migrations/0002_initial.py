# Generated by Django 4.2.2 on 2023-08-19 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('school', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sessions', to='users.teacher', verbose_name='teacher'),
        ),
        migrations.AddField(
            model_name='enrolledpackage',
            name='package_type',
            field=models.ForeignKey(help_text='Select the student package type', null=True, on_delete=django.db.models.deletion.CASCADE, to='school.packagetype', verbose_name='package type'),
        ),
        migrations.AddField(
            model_name='enrolledpackage',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrolled_packages', to='users.student', verbose_name='student'),
        ),
    ]
