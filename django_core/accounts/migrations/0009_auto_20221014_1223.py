# Generated by Django 3.1.7 on 2022-10-14 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20221013_2116'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Profile', 'verbose_name_plural': 'Profiles'},
        ),
        migrations.AlterModelOptions(
            name='scientificdirector',
            options={'verbose_name': 'ScientificDirector', 'verbose_name_plural': 'ScientificDirectors'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterModelOptions(
            name='userrole',
            options={'verbose_name': 'UserRole', 'verbose_name_plural': 'UserRoles'},
        ),
        migrations.AddField(
            model_name='profile',
            name='university_position',
            field=models.CharField(choices=[('Студент', 'Student'), ('Стажер', 'Intern'), ('Лаборант', 'Laboratory Assistant'), ('Инженер', 'Engineer'), ('Мл. научный сотрудник', 'Jun Research Assistant')], default='Студент', max_length=40),
        ),
        migrations.AlterField(
            model_name='profile',
            name='first_name',
            field=models.CharField(max_length=63),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=6),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_name',
            field=models.CharField(max_length=63),
        ),
        migrations.AlterField(
            model_name='profile',
            name='middle_name',
            field=models.CharField(max_length=63),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
