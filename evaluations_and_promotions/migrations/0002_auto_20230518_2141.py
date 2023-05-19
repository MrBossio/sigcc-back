# Generated by Django 3.1.3 on 2023-05-19 02:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('evaluations_and_promotions', '0001_initial'),
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='evaluated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeEvaluated', to='login.employee'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='evaluationType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluations_and_promotions.evaluationtype'),
        ),
        migrations.AddField(
            model_name='evaluation',
            name='evaluator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employeeEvaluator', to='login.employee'),
        ),
        migrations.AddField(
            model_name='category',
            name='evaluationType',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluations_and_promotions.evaluationtype'),
        ),
        migrations.AddField(
            model_name='areaxposicion',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluations_and_promotions.area'),
        ),
        migrations.AddField(
            model_name='areaxposicion',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluations_and_promotions.position'),
        ),
        migrations.AddField(
            model_name='area',
            name='roles',
            field=models.ManyToManyField(through='evaluations_and_promotions.AreaxPosicion', to='evaluations_and_promotions.Position'),
        ),
        migrations.AddField(
            model_name='area',
            name='supervisorsArea',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluations_and_promotions.area'),
        ),
    ]