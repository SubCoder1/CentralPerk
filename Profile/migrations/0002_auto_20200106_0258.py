# Generated by Django 2.2.4 on 2020-01-05 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='monitor_task_id',
            field=models.CharField(blank=True, default='', max_length=60, null=True),
        ),
    ]
