# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from AUth.models import User

@shared_task
def update_user_activity(username, login_ip):
    user = User.objects.get(username=username)
    user.active = True
    user.last_login_ip = login_ip
    user.save()
    return "complete :)"