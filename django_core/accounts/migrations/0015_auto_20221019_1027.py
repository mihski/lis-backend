# Generated by Django 3.1.7 on 2022-10-19 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20221019_1026'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileAvatarBrows',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=6)),
                ('usual_part', models.ImageField(default='woman_parts/Brows/1 type/Woman-1-brows-usual-light@4x.png', upload_to='body_part/brows/')),
                ('fair_part', models.ImageField(default='woman_parts/Brows/1 type/Woman-1-brows-fair-light@4x.png', upload_to='body_part/brows/')),
                ('happy_part', models.ImageField(default='woman_parts/Brows/1 type/Woman-1-brows-happy-light@4x.png', upload_to='body_part/brows/')),
                ('angry_part', models.ImageField(default='woman_parts/Brows/1 type/Woman-1-brows-angry-light@4x.png', upload_to='body_part/brows/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProfileAvatarCloth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=6)),
                ('usual_part', models.ImageField(upload_to='body_part/heads/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProfileAvatarFace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=6)),
                ('usual_part', models.ImageField(default='woman_parts/Face/1 type/Woman-1-face-usual@4x.png', upload_to='body_part/faces/')),
                ('fair_part', models.ImageField(default='woman_parts/Face/1 type/Woman-1-face-fair@4x.png', upload_to='body_part/faces/')),
                ('happy_part', models.ImageField(default='woman_parts/Face/1 type/Woman-1-face-happy@4x.png', upload_to='body_part/faces/')),
                ('angry_part', models.ImageField(default='woman_parts/Face/1 type/Woman-1-face-angry@4x.png', upload_to='body_part/faces/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProfileAvatarHair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=6)),
                ('front_part', models.ImageField(default='woman_parts/Hair/1 type/Woman-1-hair-front-red@4x.png', upload_to='body_part/hairs/')),
                ('back_part', models.ImageField(blank=True, default='woman_parts/Hair/1 type/Woman-1-hair-back-red@4x.png', null=True, upload_to='body_part/hairs/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProfileAvatarHead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=6)),
                ('usual_part', models.ImageField(default='woman_parts/Head/1 type/Woman-1-head@4x.png', upload_to='body_part/heads/')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='brows_form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarbrows'),
        ),
        migrations.AddField(
            model_name='profile',
            name='cloth_form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarcloth'),
        ),
        migrations.AddField(
            model_name='profile',
            name='face_form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarface'),
        ),
        migrations.AddField(
            model_name='profile',
            name='hair_form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarhair'),
        ),
        migrations.AddField(
            model_name='profile',
            name='head_form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.profileavatarhead'),
        ),
    ]
