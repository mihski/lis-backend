# Generated by Django 3.1.7 on 2022-11-17 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_auto_20221107_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileavatarbrows',
            name='type',
            field=models.CharField(choices=[('CUT', 'Cut'), ('ELEVATED', 'Elevated')], default='', max_length=20),
            preserve_default=False,
        ),
    ]
