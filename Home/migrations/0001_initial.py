# Generated by Django 2.2.4 on 2019-10-10 17:21

import Home.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PostModel',
            fields=[
                ('likes_count', models.PositiveIntegerField(default=0)),
                ('comment_count', models.PositiveIntegerField(default=0)),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('post_id', models.CharField(db_index=True, default='', editable=False, max_length=10)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('status_caption', models.CharField(blank=True, max_length=500)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('pic', models.ImageField(blank=True, upload_to=Home.models.pic_directory_path)),
                ('pic_thumbnail', models.ImageField(blank=True, upload_to=Home.models.thumb_directory_path)),
                ('saved_by', models.ManyToManyField(default=1, related_name='saved_by', to=settings.AUTH_USER_MODEL)),
                ('send_to', models.ManyToManyField(default=1, related_name='connections', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post',
                'ordering': ('-date_time',),
            },
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notif_id', models.CharField(blank=True, default='', max_length=65, null=True)),
                ('private_request', models.BooleanField(default=False, null=True)),
                ('private_request_id', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('reaction', models.CharField(choices=[('Liked', 'Liked'), ('Commented', 'Commented'), ('Mentioned', 'Mentioned'), ('Sent Follow Request', 'Sent Follow Request'), ('Accept Follow Request', 'Accept Follow Request'), ('Replied', 'Replied')], max_length=20)),
                ('poked_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='reacting_user')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post', to='Home.PostModel')),
                ('user_to_notify', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='to_notify')),
            ],
            options={
                'ordering': ('-date_time',),
            },
        ),
        migrations.CreateModel(
            name='PostLikes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('post_obj', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='post_like_obj', to='Home.PostModel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='liked_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post_Like',
            },
        ),
        migrations.CreateModel(
            name='PostComments',
            fields=[
                ('comment_id', models.CharField(default='', editable=False, max_length=10, primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('parent', models.BooleanField(default=True)),
                ('post_obj', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='post_comment_obj', to='Home.PostModel')),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='Home.PostComments')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='comment_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post_Comment',
                'ordering': ('date_time',),
            },
        ),
    ]
