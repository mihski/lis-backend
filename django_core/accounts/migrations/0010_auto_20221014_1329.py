# Generated by Django 3.1.7 on 2022-10-14 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20221014_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='scientific_director',
            #field=models.ForeignKey('lessons.NPC', on_delete=models.SET_NULL, null=True, blank=True)
        ),
        migrations.RemoveField(
            model_name='profile',
            name='head_form',
            #field=models.CharField(max_length=15, blank=True)
        ),
        migrations.RemoveField(
            model_name='profile',
            name='face_form',
            #field=models.CharField(max_length=15, blank=True)
        ),
        migrations.RemoveField(
            model_name='profile',
            name='hair_form',
            #field=models.CharField(max_length=15, blank=True)
        ),
        migrations.RemoveField(
            model_name='profile',
            name='dress_form',
            #field=models.CharField(max_length=15, blank=True)
        ),
    ]
