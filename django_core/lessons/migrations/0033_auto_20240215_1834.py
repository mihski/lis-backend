# Generated by Django 3.1.7 on 2024-02-15 15:34

from django.db import migrations, models
import lessons.models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0032_auto_20221122_2350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='locale',
            field=models.JSONField(default=lessons.models.default_locale),
        ),
        migrations.AlterField(
            model_name='inputblock',
            name='correct',
            field=models.JSONField(default=lessons.models.default_locale),
        ),
        migrations.AlterField(
            model_name='lessonblock',
            name='locale',
            field=models.JSONField(default=lessons.models.default_locale),
        ),
        migrations.AlterField(
            model_name='lessonblock',
            name='markup',
            field=models.JSONField(default=lessons.models.default_locale),
        ),
    ]
