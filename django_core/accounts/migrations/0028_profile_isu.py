# Generated by Django 3.1.7 on 2022-11-07 08:54

import django
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_profile_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='isu',
            field=models.CharField(default='', editable=False, max_length=31),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile',
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]
