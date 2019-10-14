from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.core.files import File
from django.conf import settings
from Profile.models import User, Friends, Account_Settings
from AUth.forms import Registerform
from AUth.tasks import (
    update_user_activity_on_login, update_user_activity_on_logout, 
    erase_duplicate_sessions, check_username_validity,
    check_email_validity, check_pass_strength
    )
import json
from PIL import Image
from io import BytesIO

@csrf_protect
def user_login(request):
    context = None
    logout(request)
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if not user.is_active():
                # Celery handling the task to update user activity
                update_user_activity_on_login.delay(username, request.session.session_key)
            elif user.session_key != request.session.session_key:
                # Celery handling the task to delete sessions of same user logged in from multiple devices
                erase_duplicate_sessions.delay(username, request.session.session_key, request.session.cache_key)
            return HttpResponse(json.dumps("valid user"), content_type="application/json")
        else:
            context = "Username or Password is incorrect!"
            return HttpResponse(json.dumps(context), content_type="application/json")
    return render(request, 'login.html', context=context)

def user_logout(request):
    update_user_activity_on_logout.delay(request.user.username)
    logout(request)
    return redirect(reverse('user_login'))

@csrf_protect
def register_user(request):
    context = {}
    if request.POST:
        activity = request.POST.get('activity')
        result = None
        if activity == 'check username validity':
            username = request.POST.get('username')
            result = check_username_validity.delay(username).get()
        elif activity == 'check email validity':
            email = request.POST.get('email')
            result = check_email_validity.delay(email).get()
        elif activity == 'check pass strength':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            result = check_pass_strength.delay(password, username, email).get()
        else:
            result = {}
            form = Registerform(request.POST or None)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    Account_Settings.objects.create(user=user)
                    Friends.objects.create(current_user=user)
                    default_img = Image.open(settings.STATIC_ROOT + '/signup/img/default.png')
                    im_io = BytesIO()
                    default_img.save(im_io, format='PNG', quality=90, optimize=True)
                    user.profile_pic = File(im_io, name=f"thumb_{str(user.user_id)}.png")
                    user.save()
                    result = 'valid form'
            else:
                if form.has_error('username'):
                    result['username'] = form.errors['username']
                if form.has_error('full_name'):
                    result['full_name'] = form.errors['full_name']
                if form.has_error('gender'):
                    result['gender'] = form.errors['gender']
                if form.has_error('email'):
                    result['email'] = form.errors['email']
                if form.has_error('password'):
                    result['password'] = form.errors['password']
        return HttpResponse(json.dumps(result), content_type='application/json')
    return render(request, 'signup.html', context)