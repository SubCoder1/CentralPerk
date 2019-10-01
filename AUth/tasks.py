# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from Profile.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime
import pytz, re

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
    user.channel_name = ''
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