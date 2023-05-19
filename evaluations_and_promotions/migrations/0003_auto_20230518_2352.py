# Generated by Django 3.1.3 on 2023-05-19 04:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
        ('evaluations_and_promotions', '0002_auto_20230518_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='evaluated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeEvaluated', to='login.employee'),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='evaluator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeEvaluator', to='login.employee'),
        ),
    ]
