# Generated by Django 3.1.7 on 2022-10-21 18:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_statistics'),
        ('lessons', '0024_auto_20221020_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileLessonDone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.lesson')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
                ('finished_at', models.DateTimeField(auto_now=True))
            ],
        ),
    ]
