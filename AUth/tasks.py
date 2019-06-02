# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from Profile.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from datetime import datetime
import pytz

@shared_task
def update_user_activity_on_login(username, session_key=None):
    user = User.get_user_obj(username=username)
    user.active = True
    user.session_key = session_key
    user.save()
    return "complete :)"

@shared_task
def update_user_activity_on_logout(username):
    user = User.get_user_obj(username=username)
    user.active = False
    user.session_key = ''
    tz = pytz.timezone('Asia/Kolkata')
    user.last_login = datetime.now().astimezone(tz=tz)
    user.save()
    return "complete :)"

@shared_task
def erase_duplicate_sessions(username, session_key, cache_key):
    user = User.get_user_obj(username=username)
    previous_session = user.session_key
    Session.objects.get(session_key=previous_session).delete()
    cache.delete(f"django.contrib.sessions.cached_{cache_key}")
    user.session_key = session_key
    return "complete :)"