# Generated by Django 3.1.7 on 2022-10-23 13:52

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20221023_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='angry_image',
            field=models.ImageField(editable=False, null=True, upload_to=accounts.models._upload_avatar_image),
        ),
        migrations.AddField(
            model_name='profile',
            name='fair_image',
            field=models.ImageField(editable=False, null=True, upload_to=accounts.models._upload_avatar_image),
        ),
        migrations.AddField(
            model_name='profile',
            name='happy_image',
            field=models.ImageField(editable=False, null=True, upload_to=accounts.models._upload_avatar_image),
        ),
        migrations.AddField(
            model_name='profile',
            name='usual_image',
            field=models.ImageField(editable=False, null=True, upload_to=accounts.models._upload_avatar_image),
        ),
    ]
