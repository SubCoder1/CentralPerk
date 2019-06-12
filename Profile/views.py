from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from Profile.forms import NonAdminChangeForm
from django.core.exceptions import ObjectDoesNotExist
from Profile.models import User, Friends
from Profile.last_activity import activity
from Home.models import PostModel
from Home.tasks import send_notifications
from Home.forms import CommentForm
import json
# Create your views here.

def manage_relation(request, username, option=None):
    current_user = request.user
    follow_unfollow_user = User.get_user_obj(username=username)

    if option == 'follow':
        Friends.follow(current_user, follow_unfollow_user)
        # Notify the user to whom this follow request is being sent
        send_notifications.delay(username=current_user.username, reaction="Sent Follow Request", send_to_username=follow_unfollow_user.username)
    else:
        Friends.unfollow(current_user, follow_unfollow_user)
    return redirect(reverse('view_profile', kwargs={ 'username':username }))

def manage_profile_post_likes(request, username, post_id, view_post=None):
    try:
        post = PostModel.objects.get_post(post_id=post_id)
    except ObjectDoesNotExist:
        return render(request, 'post_500.html', {})
     
    user = request.user
    if user in post.post_like_obj.likes.all():
        # Dislike post
        post.post_like_obj.likes.remove(user)
        post.likes_count = F('likes_count') - 1
        post.save()
    else:
        # Like post
        post.post_like_obj.likes.add(user)
        post.likes_count = F('likes_count') + 1
        post.save()

        # Notify the user whose post is being liked
        send_notifications.delay(username=request.user.username, reaction="Liked", post_id=post_id)

    if view_post:
        return redirect(reverse('view_post', kwargs={ 'post_id':post_id }))

    return redirect(reverse('view_profile', kwargs={ 'username':username }))

def view_profile(request, username=None):
    try:
        user, editable = (request.user, True) if username == request.user.username else (User.objects.get(username=username), False)
    except ObjectDoesNotExist:
        return render(request, 'profile_500.html', {})
        
    user_posts = user.posts.values_list('status_caption', 'pic', 'location', 'date_time', 'likes_count', 'post_id', named=True)

    current_user, created = Friends.objects.get_or_create(current_user=user)
    isFollower, isFollowing, follow_count, follower_count = None, None, 0, 0
    if not created:
        # True if request.user follows the user he/she is searching for
        isFollowing = True if current_user.followers.filter(username=request.user).exists() else False
        if not isFollowing:
            # True if request.user is being followed by 'username'
            isFollower = True if current_user.following.filter(username=request.user).exists() else False
        
        follow_count = current_user.following.count()
        follower_count = current_user.followers.count()
    
    active = '#'
    # Ajax request/response to check user activity, shown iff requset.user follows 'username'
    if request.POST and not editable:
        ajax_request = request.POST.get("activity")
        if isFollowing and ajax_request is not None:
            if user.is_active():
                active = 'online'
            else:
                active = activity(user.last_login)
            return HttpResponse(json.dumps(active), content_type='application/json')
    elif request.POST and editable:
        return HttpResponse(json.dumps(active), content_type='application/json')
    
    context = { 'profile':user, 'posts':user_posts, 'editable':editable, 
                'isFollowing':isFollowing, 'isFollower': isFollower,
                'follow_count':follow_count, 'follower_count':follower_count, 'activity':active,
             }

    return render(request, 'profile.html', context=context)

def post_view(request, post_id):
    if request.POST:
        form = CommentForm(request.POST or None)
        if form.is_valid():
            post_comment = form.save(commit=False)
            post_comment.post_obj = PostModel.objects.get_post(post_id=request.POST.get('post_id'))
            post_comment.user = request.user
            post_comment.comment = form.cleaned_data.get('comment')
            post_comment.save()
    try:
        post_obj = PostModel.objects.get_post(post_id=post_id)
        post_likes_list = post_obj.post_like_obj.likes.all().values_list('username', 'profile_pic', named=True)
        post_comments = post_obj.post_comment_obj.values_list('user__username', 'user__profile_pic', 'comment', 'date_time', named=True)
    except ObjectDoesNotExist:
        return render(request, 'profile_500.html', {})

    editable = False
    if post_obj.user.username == request.user.username:
        editable = True
    
    context = { 'post_data':post_obj, 'post_id': post_id, 'like_list':post_likes_list, 'editable':editable, 'comments':post_comments }
    return render(request, 'view_post.html', context=context)

def del_user_post(request, post_id):
    try:
        request.user.posts.get(post_id=post_id).delete()
    except ObjectDoesNotExist:
        pass
    return redirect(reverse('view_profile', kwargs={ 'username':request.user.username }))

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
            return redirect(reverse('view_profile', kwargs={ 'username':username }))
        elif change_pass_form.is_valid():
            change_pass_form.save()
            update_session_auth_hash(request, change_pass_form.user)  # This method keeps the user logged-in even after changing the password
            return redirect(reverse('view_profile', kwargs={ 'username':username }))

        context = { 'edit_form':edit_form, 'change_pass_form':change_pass_form }
        return render(request, self.template_name, context)