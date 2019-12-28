# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from Profile.models import User, Friends
from Home.models import Conversations
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import AsyncToSync
from centralperk.celery import app
from datetime import datetime
from hashlib import sha256
import pytz, re
from itertools import chain

@shared_task
def update_open_convo(username, activity):
    try:
        user = User.get_user_obj(username=username)
        channel_layer = get_channel_layer()

        query_a = Q(user_a=user)
        query_a.add(Q(chat_active_from_b=True), Q.AND)
        open_convo_list_a = Conversations.objects.filter(query_a).select_related('user_b')
        if len(open_convo_list_a):
            for open_convo in open_convo_list_a:
                convo_id = sha256(bytes(str(open_convo.id), encoding='utf-8')).hexdigest()
                context = { 
                    "type":"update.p.chat", "convo_unique_id":convo_id, "activity":activity,
                }
                AsyncToSync(channel_layer.send)(open_convo.user_b.channel_name, context)

        query_b = Q(user_b=user)
        query_b.add(Q(chat_active_from_a=True), Q.AND)
        open_convo_list_b = Conversations.objects.filter(query_b).select_related('user_a')
        if len(open_convo_list_b):
            for open_convo in open_convo_list_b:
                convo_id = sha256(bytes(str(open_convo.id), encoding='utf-8')).hexdigest()
                context = { 
                    "type":"update.p.chat", "convo_unique_id":convo_id, "activity":activity,
                }
                AsyncToSync(channel_layer.send)(open_convo.user_a.channel_name, context)
    finally:
        close_old_connections()

@shared_task
def close_open_convo(username):
    try:
        user = User.get_user_obj(username=username)
        # Build query
        query_a = Q(user_a=user)
        query_a.add(Q(chat_active_from_a=True), Q.AND)
        open_convo_list_a = Conversations.objects.filter(query_a)
        query_b = Q(user_b=user)
        query_b.add(Q(chat_active_from_b=True), Q.AND)
        open_convo_list_b = Conversations.objects.filter(query_b)

        open_convo_list = list(chain(open_convo_list_a, open_convo_list_b))
        #print(open_convo_list)
        for convo in open_convo_list:   # Theoretically this loop should run for at most 1 times
            if convo.user_a == user:
                convo.chat_active_from_a = False
            else:
                convo.chat_active_from_b = False
            convo.save()
        return "closed open conversations :)"
    finally:
        close_old_connections()

@shared_task
def update_user_activity_on_login(username, session_key=None):
    try:
        user = User.get_user_obj(username=username)
        user.active = True
        user.session_key = session_key
        user.save()
        # show any friend of request.user that he/she's online
        # i.e., change activity in any open conversation from other end
        update_open_convo.delay(username=username, activity='login')
        return "complete :)"
    finally:
        close_old_connections()

@shared_task
def update_user_activity_on_logout(username):
    try:
        user = User.get_user_obj(username=username)
        user.session_key = ''
        user.channel_name = ''
        user.active = False
        if user.just_created == True:
            user.just_created = False
        tz = pytz.timezone('Asia/Kolkata')
        user.last_login = datetime.now().astimezone(tz=tz)
        if user.monitor_task_id is not "":
            # revoke any ongoing session monitoring task against this user.
            app.control.revoke(str(user.monitor_task_id))
            user.monitor_task_id = ""
        user.save()
        # Close any open conversations from this end
        close_open_convo.delay(username=username)
        update_open_convo.delay(username=username, activity='logout')
        return "complete :)"
    finally:
        close_old_connections()

@shared_task
def erase_duplicate_sessions(username, session_key, cache_key):
    try:
        user = User.get_user_obj(username=username)
        previous_session = user.session_key
        Session.objects.get(session_key=previous_session).delete()
        cache.delete(f"django.contrib.sessions.cached_{cache_key}")
        user.session_key = session_key
        user.save()
        return "complete :)"
    except:
        return 'session not found :('
    finally:
        close_old_connections()

@shared_task
def check_username_validity(username, logged_in_user=None):
    # Only for edit_profile username validity corner case
    if username == logged_in_user:
        return 'same username'
    # check validity of username
    if len(str(username)) < 5:
        # username less than 5 characters
        return 'Username should be > 5 characters'
    elif len(str(username)) > 20:
        # username exceeded max_limit of 20 characters
        return 'Username should be < 21 characters'
    elif str(username).isspace():
        # username consists of spaces
        return 'Username should consist only letters & numbers'
    elif re.findall('[^A-Za-z0-9]', str(username)) and '_' not in re.findall('[^A-Za-z0-9]', str(username)):
        # username consists of special characters (excluding '_')
        return "Special characters allowed -> '_'"
    elif User.objects.filter(username=username).exists():
        # someone is using this username
        return 'This username is taken'
    return 'valid username'

@shared_task
def check_email_validity(email):
    try:
        validate_email(email)
        if len(str(email)) > 254:
            return 'Email should be < 255 characters'
        elif User.objects.filter(email=email).exists():
            return 'This Email is being used by another user'  
        return 'valid email'
    except ValidationError:
        return 'invalid email'
    finally:
        close_old_connections()

@shared_task
def check_fullname_validity(full_name):
    if not len(full_name):
        return 'Full name cannot be empty'
    full_name_cleaned = str(full_name).replace(" ", "")
    if str(full_name).isspace():
        return 'Full name should not consist of only spaces'
    elif not re.match("^[a-zA-Z0-9_]*$", full_name_cleaned):
        return 'Full name should consist only letters'
    else:
        return 'valid fullname'

@shared_task
def check_pass_strength(password, username=None, email=None):
    try:
        if str(password).isspace():
            return 'invalid password'
        user = None
        if username is not None or email is not None:
            user = User(username=username, email=email)
        validate_password(password, user=user)
        if not re.findall('[^A-Za-z0-9]', str(password)):
            return 'strength:medium, use special characters'
        elif str(password).isalpha():
            return 'strength:medium, use numbers'
        else:
            return 'strong password'
    except ValidationError as issues:
        if 'This password is too short. It must contain at least 8 characters.' in issues:
            return 'strength:bad, should be > 8 characters'
        elif 'This password is too common.' in issues:
            return 'strength:bad, too common'
        elif 'This password is entirely numeric.' in issues:
            return 'strength:bad, too numeric'
        elif 'The password is too similar to the username.' in issues:
            return 'strength:medium, too similar to username'
        elif 'The password is too similar to the email.' in issues:
            return 'strength:medium, too similar to email'
        else:
            return 'strength:bad'
    finally:
        close_old_connections()