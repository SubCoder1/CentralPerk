from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from AUth.tasks import check_username_validity, check_email_validity, check_fullname_validity
from Profile.forms import NonAdminChangeForm, CustomPasswordChangeForm
from Profile.models import User, Friends, Account_Notif_Settings
from Profile.tasks import update_user_acc_settings, manage_likes
from Home.models import PostModel, PostComments, PostLikes
from Home.tasks import send_notifications, del_notifications
from Home.forms import CommentForm
import json
# Create your views here.

def manage_relation(request, username, option=None):
    current_user = request.user
    follow_unfollow_user = User.get_user_obj(username=username)
    result = {}
    if option in ('follow', 'follow_back'):
        Friends.follow(current_user, follow_unfollow_user)
        # Notify the user to whom this follow request is being sent
        send_notifications.delay(username=current_user.username, reaction="Sent Follow Request", send_to_username=follow_unfollow_user.username)
        result["option"] = 'Unfollow'
    else:
        Friends.unfollow(current_user, follow_unfollow_user)
        # Delete any follow requests sent to follow_unfollow_usrname
        del_notifications.delay(username=current_user.username, reaction="Sent Follow Request", send_to_username=follow_unfollow_user.username)
        result["option"] = 'Follow'
    
    friend = Friends.objects.get(current_user=follow_unfollow_user)
    result["follower_count"], result["following_count"] = friend.followers.count(), friend.following.count()
    return HttpResponse(json.dumps(result), content_type="application/json")

def manage_post_likes(request, post_id):
    if request.is_ajax():
        action = request.POST.get('action')
        if action == 'liked':
            action = "Liked the post!"
        else:
            action = "Disliked the post!"
        manage_likes.delay(post_id, str(request.user.username))
        return HttpResponse(json.dumps({"status": "ready to update", "action":action}), content_type="application/json")

def view_profile(request, username=None):
    try:
        user, editable = (request.user, True) if username == request.user.username else (User.objects.get(username=username), False)
    except ObjectDoesNotExist:
        return render(request, 'profile_500.html', {})

    user_posts = user.posts.all()
    saved_posts = user.saved_by.all()

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

    if request.is_ajax():
        ajax_request = request.POST.get("activity")
        if ajax_request == 'get_user_acc_settings':
            # send current user account settings
            user_acc_settings = Account_Notif_Settings.objects.get(user=request.user)
            context = { 'disable_all':user_acc_settings.disable_all, 'p_likes':user_acc_settings.p_likes, 
            'p_comments':user_acc_settings.p_comments, 'f_requests':user_acc_settings.f_requests,
            'p_comment_likes': user_acc_settings.p_comment_likes, 'private_acc':user_acc_settings.private_acc,
            'activity_status': user_acc_settings.activity_status, }
            return HttpResponse(json.dumps(context), content_type='application/json')
        elif ajax_request == 'set_user_acc_settings':
            # set current user account settings from data sent by client
            data = {'disable_all': request.POST.get('disable_all'), 'p_likes': request.POST.get('p_likes'),
            'p_comments': request.POST.get('p_comments'), 'p_comment_likes': request.POST.get('p_comment_likes'),
            'f_requests': request.POST.get('f_requests'), 'private_acc': request.POST.get('private_acc'),
            'activity_status': request.POST.get('activity_status'), }
            update_user_acc_settings.delay(username=username, data=data)
    
    context = { 'profile':user, 'posts':user_posts, 'saved_posts':saved_posts, 'editable':editable, 
                'isFollowing':isFollowing, 'isFollower': isFollower,
                'follow_count':follow_count, 'follower_count':follower_count,
             }

    return render(request, 'profile.html', context=context)

def post_view(request, post_id):
    post_obj = PostModel.objects.get_post(post_id=post_id)
    if post_obj is None:
        return render(request, 'post_500.html', {})

    if request.is_ajax():
        try:
            post_obj = PostModel.objects.get_post(post_id=post_id)
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps("post doesn't exist"), content_type="application/json")

        if request.GET.get('activity') == 'refresh comments':
            post_comments, comment_count = post_obj.post_comment_obj.get_comments(post_obj)
            post_comments_html = render_to_string("post_comments.html", {'comments':post_comments})
            return HttpResponse(json.dumps({"post_comments_html":post_comments_html, "comment_count":comment_count}), content_type="application/json")
        if request.GET.get('activity') == 'refresh likes':
            post_likes_list = post_obj.post_like_obj.select_related('user')
            post_likes_html = render_to_string("post_likes.html", {"liked_user_list":post_likes_list})
            return HttpResponse(json.dumps({"post_likes_html":post_likes_html, "likes_count":len(post_likes_list)}), content_type="application/json")
        if request.POST.get('activity') == 'add comment':
            form = CommentForm(request.POST or None)
            result = None
            if form.is_valid():
                post_obj = PostModel.objects.get_post(post_id=post_id)
                reply = str(request.POST.get('reply'))
                if "_" in reply:
                    index = reply.index("_")
                    comment_id, reply_id = reply[:index], reply[index+1:len(reply)]
                else:
                    comment_id = reply
                    reply_id = None

                if comment_id == '':
                    # request.user commented on a post with post_id=post_id
                    post_obj.post_comment_obj.add(PostComments.objects.create(user=request.user, 
                    post_obj=post_obj, comment=form.cleaned_data.get('comment')))
                    send_notifications.delay(username=request.user.username, reaction='Commented', send_to_username=post_obj.user.username, post_id=post_id)
                else:
                    # request.user replied to someone's comment on post with post_id=post_id
                    try:
                        parent_comment = PostComments.objects.get(comment_id=comment_id)
                        reply = form.cleaned_data.get('comment')
                        parent_comment.replies.add(PostComments.objects.create(user=request.user,
                        post_obj=post_obj, comment=reply, parent=False))
                        send_notifications.delay(username=request.user.username, reaction='Replied', send_to_username=reply_id)
                    except ObjectDoesNotExist:
                        pass
                post_obj.comment_count = F('comment_count') + 1
                post_obj.save()
                post_obj.refresh_from_db()
                result = "ready to update"
            else:
                result = "save unsuccessful"
            return HttpResponse(json.dumps(result), content_type='application/json')

    post_likes_list = post_obj.post_like_obj.select_related('user')
    post_comments, comment_count = post_obj.post_comment_obj.get_comments(post_obj)

    editable = False
    if post_obj.user == request.user:
        editable = True
    
    liked_by_user = False
    if post_obj.post_like_obj.filter(user=request.user).exists():
        liked_by_user = True
    
    context = { 'post_data':post_obj, 'post_id': post_id, 
    'liked_user_list':post_likes_list, 'editable':editable, 
    'comments':post_comments, 'comment_count':comment_count,
    'liked_by_user':liked_by_user }

    return render(request, 'view_post.html', context=context)

def del_user_post(request, post_id):
    try:
        request.user.posts.get_post(post_id=post_id).delete()
    except ObjectDoesNotExist:
        pass
    return redirect(reverse('view_profile', kwargs={ 'username':request.user.username }))

class edit_profile(TemplateView):
    template_name = 'edit_profile.html'

    def get(self, request, username):
        edit_form = NonAdminChangeForm(instance=request.user)
        change_pass_form = CustomPasswordChangeForm(user=request.user)
        context = { 'edit_form':edit_form,'change_pass_form':change_pass_form }
        return render(request, self.template_name, context)

    def post(self, request, username):
        result = {}
        activity = request.POST.get('activity')
        # ------------ profile-edit request handling ------------
        if activity == 'validate_profile_data':
            edit_form = NonAdminChangeForm(request.POST or None, request.FILES or None, instance=request.user)
            if edit_form.is_valid():
                edit_form.save()
                result = 'valid edit_prof_form'
            else:
                if edit_form.has_error('username'):
                    result['username'] = edit_form.errors['username']
                if edit_form.has_error('full_name'):
                    result['full_name'] = edit_form.errors['full_name']
                if edit_form.has_error('email'):
                    result['email'] = edit_form.errors['email']
                if edit_form.has_error('birthdate'):
                    result['birthdate'] = edit_form.errors['birthdate']
                if edit_form.has_error('gender'):
                    result['gender'] = edit_form.errors['gender']
                if edit_form.has_error('bio'):
                    result['bio'] = edit_form.errors['bio']
        # ------------ change password request handling ------------
        elif activity == 'validate_new_password':
            change_pass_form = CustomPasswordChangeForm(data=request.POST or None, user=request.user) # For changing password only
            if change_pass_form.is_valid():
                change_pass_form.save()
                update_session_auth_hash(request, change_pass_form.user) # This method keeps the user logged-in even after changing the password
                result = 'valid change_pass_form'
            else:
                if change_pass_form.has_error('old_password'):
                    result['old_password'] = change_pass_form.errors['old_password']
                if change_pass_form.has_error('new_password1'):
                    result['new_password1'] = change_pass_form.errors['new_password1']
                if change_pass_form.has_error('new_password2'):
                    result['new_password2'] = change_pass_form.errors['new_password2']
        return HttpResponse(json.dumps(result), content_type='application/json')