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
            #return redirect('/home/')
            return redirect('/admin/')
        else:
            context = { 'error':"Username or Password is incorrect!" }
    return render(request, 'login.html', context=context)

@csrf_protect
def register_user(request):
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
                return redirect('/admin/')
    context = { 'form': form }
    return render(request, 'signup.html', context)

"""def view_profile(request, email):
    obj = User.objects.get(email=email)
    context = { 'object':obj, 'user':request.user }
    return render(request, 'profile.html', context)"""
