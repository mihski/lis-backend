# Generated by Django 3.1.7 on 2022-11-22 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0031_auto_20221115_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='start_energy',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='start_money',
            field=models.IntegerField(default=500),
        ),
    ]
