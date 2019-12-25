# Generated by Django 2.2.4 on 2019-12-21 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0002_conversations'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversations',
            name='sent_by_a_count',
            field=models.BigIntegerField(default=0, verbose_name='msg_sent_by_user_a'),
        ),
        migrations.AddField(
            model_name='conversations',
            name='sent_by_b_count',
            field=models.BigIntegerField(default=0, verbose_name='msg_sent_by_user_b'),
        ),
    ]
