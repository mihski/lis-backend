# Generated by Django 3.1.7 on 2022-09-07 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0009_auto_20220830_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='radiosblock',
            name='correct',
            field=models.CharField(max_length=127),
        ),
    ]