# Generated by Django 3.1.7 on 2023-07-30 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_auto_20221123_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='language',
            field=models.CharField(choices=[('ru', 'RU'), ('en', 'EN')], default='ru', max_length=8),
        ),
    ]
