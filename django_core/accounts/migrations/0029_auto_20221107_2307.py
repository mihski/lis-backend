# Generated by Django 3.1.7 on 2022-11-07 20:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0028_profile_isu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='brows_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarbrows'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cloth_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarclothes'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='face_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarface'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='hair_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarhair'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='head_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarhead'),
        ),
    ]
