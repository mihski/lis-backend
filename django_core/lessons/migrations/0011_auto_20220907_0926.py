# Generated by Django 3.1.7 on 2022-09-07 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0010_auto_20220907_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputblock',
            name='correct',
            field=models.JSONField(default={'en': [], 'ru': []}),
        ),
    ]
