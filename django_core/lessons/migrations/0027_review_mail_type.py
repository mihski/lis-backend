# Generated by Django 3.1.7 on 2022-10-25 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0026_auto_20221025_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='mail_type',
            field=models.CharField(choices=[('content', 'Content'), ('tech', 'Tech')], default='content', max_length=7),
        ),
    ]
