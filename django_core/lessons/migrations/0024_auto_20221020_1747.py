# Generated by Django 3.1.7 on 2022-10-20 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0023_auto_20221018_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='bonuses',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='laboratory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lessons.laboratory'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='quest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lessons', to='lessons.quest'),
        ),
    ]
