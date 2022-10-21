# Generated by Django 3.1.7 on 2022-10-21 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20221020_0315'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quests_done', models.IntegerField(default=0)),
                ('lessons_done', models.IntegerField(default=0)),
                ('total_time_spend', models.IntegerField(default=0)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='accounts.profile')),
            ],
            options={
                'verbose_name': 'ProfileStatistics',
                'verbose_name_plural': 'ProfilesStatistics',
            },
        ),
    ]
