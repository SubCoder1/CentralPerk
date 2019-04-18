from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import update_session_auth_hash
from Profile.forms import NonAdminChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from AUth.models import User
from Profile.models import Friends

# Create your views here.

def manage_relation(request, username, option=None):
    current_user = request.user
    follow_unfollow_user = User.objects.get(username=username)

    if option == 'follow':  
        Friends.follow(current_user, follow_unfollow_user)
    else:
        Friends.unfollow(current_user, follow_unfollow_user)
    return view_profile(request, username=username)

def view_profile(request, username=None):
    user, editable = (request.user, True) if username == request.user.username else (User.objects.get(username=username), False)
    user_posts = user.postmodel_set.values_list('status', 'location', 'date_time', named=True)
    return render(request, 'profile.html', { 'profile':user, 'posts':user_posts, 'edit':editable, })

class edit_profile(TemplateView):
    template_name = 'edit_profile.html'

    def get(self, request, username):
        edit_form = NonAdminChangeForm(instance=request.user)
        change_pass_form = PasswordChangeForm(user=request.user)
        context = { 'edit_form':edit_form,'change_pass_form':change_pass_form }
        return render(request, self.template_name, context)
    
    def post(self, request, username):
        edit_form = NonAdminChangeForm(request.POST or None, instance=request.user)
        change_pass_form = PasswordChangeForm(data=request.POST or None, user=request.user) # For changing password only
        if edit_form.is_valid():
            edit_form.save()
            return redirect('/profile/{username}'.format(username=username))
        elif change_pass_form.is_valid():
            change_pass_form.save()
            update_session_auth_hash(request, change_pass_form.user)  # This method keeps the user logged-in even after changing the password
            return redirect('/profile/{username}'.format(username=username))

        context = { 'edit_form':edit_form,'change_pass_form':change_pass_form }
        return render(request, self.template_name, context)