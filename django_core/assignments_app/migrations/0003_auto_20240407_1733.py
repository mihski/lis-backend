# Generated by Django 3.1.7 on 2024-04-07 14:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_auto_20240407_1733'),
        ('assignments_app', '0002_auto_20240215_1928'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assignment',
            options={'verbose_name': 'Итоговое задание', 'verbose_name_plural': 'Итоговые задания'},
        ),
        migrations.AlterModelOptions(
            name='studentassignment',
            options={'verbose_name': 'Студенческое задание', 'verbose_name_plural': 'Студенческие задания'},
        ),
        migrations.AlterField(
            model_name='assignment',
            name='description',
            field=models.TextField(verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='max_score',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(10)], verbose_name='максимальный балл'),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='title',
            field=models.CharField(max_length=100, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='accepted',
            field=models.BooleanField(default=False, verbose_name='принято'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='answer',
            field=models.TextField(validators=[django.core.validators.URLValidator()], verbose_name='ответ'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='assignment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assignments_app.assignment', verbose_name='задание'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='completed_date',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='дата выполнения'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='accounts.profile', verbose_name='профиль'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='reviewe',
            field=models.TextField(blank=True, null=True, verbose_name='отзыв'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='reviewed',
            field=models.BooleanField(default=False, verbose_name='проверено'),
        ),
        migrations.AlterField(
            model_name='studentassignment',
            name='score',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(10)], verbose_name='балл'),
        ),
    ]