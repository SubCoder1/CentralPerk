from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from AUth.models import User
from AUth.forms import Registerform

@csrf_protect
def user_login(request):
    context = {}
    logout(request)
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            user.active = True
            user.save()
            login(request, user)
            return redirect('/home/')
        else:
            context = { 'error':"Username or Password is incorrect!" }
    return render(request, 'login.html', context=context)

def user_logout(request):
    user = request.user
    user.active = False
    user.save()
    logout(request)
    return redirect('/')

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
                #return redirect('/home/')
                return redirect('/home/')
    else:
        if form.has_error('username'):
            context['username'] = 'already exists!'
        if form.has_error('email'):
            context['email'] = 'already exists!'
    return render(request, 'signup.html', context)
