# Generated by Django 2.2.4 on 2019-10-23 13:12

import Profile.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_key', models.CharField(default='notyetaccquired', max_length=40)),
                ('channel_name', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('username', models.CharField(default='', max_length=20, unique=True)),
                ('full_name', models.CharField(max_length=50)),
                ('birthdate', models.CharField(max_length=10)),
                ('bio', models.TextField(blank=True, default='I am breathtaking!', max_length=160)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=20)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('just_created', models.BooleanField(default=True)),
                ('profile_pic', models.ImageField(blank=True, upload_to=Profile.models.user_directory_path)),
                ('admin', models.BooleanField(default=False)),
                ('staff', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_user', to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('following', models.ManyToManyField(related_name='following', to=settings.AUTH_USER_MODEL)),
                ('pending', models.ManyToManyField(related_name='pending_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Relation',
            },
        ),
        migrations.CreateModel(
            name='Account_Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disable_all', models.BooleanField(default=False)),
                ('p_likes', models.CharField(choices=[('Disable', 'Disable'), ('From People I Follow', 'From People I Follow'), ('From Everyone', 'From Everyone')], default='From Everyone', max_length=21, verbose_name='Post Likes')),
                ('p_comments', models.CharField(choices=[('Disable', 'Disable'), ('From People I Follow', 'From People I Follow'), ('From Everyone', 'From Everyone')], default='From Everyone', max_length=21, verbose_name='Post Comments')),
                ('p_comment_likes', models.CharField(choices=[('Disable', 'Disable'), ('From People I Follow', 'From People I Follow'), ('From Everyone', 'From Everyone')], default='Disable', max_length=21, verbose_name='Post Comment Likes')),
                ('f_requests', models.BooleanField(default=False)),
                ('private_acc', models.BooleanField(default=False, null=True)),
                ('activity_status', models.BooleanField(default=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_setting', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Setting',
            },
        ),
    ]
