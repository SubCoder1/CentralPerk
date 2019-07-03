from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from Profile.models import User
from Profile.forms import Registerform
from AUth.tasks import update_user_activity_on_login, update_user_activity_on_logout, erase_duplicate_sessions
import json

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
    form = Registerform(request.POST or None)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('home_view'))
    else:
        if form.has_error('username'):
            context['username'] = 'already exists!'
        if form.has_error('email'):
            context['email'] = 'already exists!'
    return render(request, 'signup.html', context)