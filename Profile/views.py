from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.db import transaction
from django.core.files import File
from django.contrib.sessions.models import Session
from django.db import close_old_connections
from django.contrib.auth import logout
from AUth.tasks import check_username_validity, check_email_validity, check_fullname_validity
from Profile.forms import NonAdminChangeForm, CustomPasswordChangeForm
from Profile.models import User, Friends, Account_Settings
from Profile.tasks import update_user_acc_settings, create_or_update_convo_obj
from Home.models import PostModel, PostComments, PostLikes, Conversations
from Home.tasks import send_notifications, del_notifications, share_post_to_users
from Home.forms import CommentForm
import json, os, pytz
from PIL import Image
from io import BytesIO
from datetime import datetime, timedelta
# Create your views here.

def manage_relation(request, username, option=None):
    """ 
        This view handles follow/unfollow/block requests from client against an user with username.
        ----- args -----
        username -> The user whom request.user is trying to follow/unfollow/block
        option -> Is he/she trying to follow/unfollow/block the user

        RETURNS -> An HttpResponse with Count of followers, following of the user(username), with a change in option
        (follow->unfollow, block->unblock & vice-versa)
    """
    try:
        current_user = request.user
        follow_unfollow_user = User.get_user_obj(username=username)
        user_acc_settings = Account_Settings.objects.get(user=follow_unfollow_user)
        result = {}
        if option in ('follow', 'follow_back'):
            if user_acc_settings.private_acc:
                send_notifications.delay(username=current_user.username, reaction="Sent Follow Request", send_to_username=follow_unfollow_user.username, private_request=True)
                Friends.add_to_pending(current_user, follow_unfollow_user)
                result["option"] = 'Requested'
            else:
                if option == 'follow':
                    # Create a conversation model btw current_user & follow_unfollow_user (if doesn't exist already)
                    create_or_update_convo_obj.delay(current_user.username, follow_unfollow_user.username, 'follow')
                send_notifications.delay(username=current_user.username, reaction="Sent Follow Request", send_to_username=follow_unfollow_user.username, private_request=False)
                Friends.follow(current_user, follow_unfollow_user)
                # share two of follow_unfollow_user's recent posts *(if any) to request.user's wall
                share_post_to_users.delay(username=follow_unfollow_user.username, send_to=[str(current_user.username)], to_wall=True)
                result["option"] = 'Unfollow'
        else:
            Friends.unfollow(current_user, follow_unfollow_user)
            if user_acc_settings.private_acc:
                # To deny users to view posts of they just unfollowed.
                # Only if the user whom request.user unfollowed has a private account.
                # This will remove follow_unfollow_user's posts from request.user's wall (if any)
                request.user.connections.remove(*PostModel.objects.filter(user=follow_unfollow_user))
                result['prof_posts'] = render_to_string('prof_posts.html', {'posts':None})
                Friends.rm_from_pending(current_user, follow_unfollow_user)
            # Delete any follow requests sent to follow_unfollow_usrname
            del_notifications.delay(username=current_user.username, reaction="Sent Follow Request", send_to_username=follow_unfollow_user.username)
            create_or_update_convo_obj.delay(current_user.username, follow_unfollow_user.username, 'unfollow')
            result["option"] = 'Follow'
        
        friend = Friends.objects.get(current_user=follow_unfollow_user)
        result["follower_count"], result["following_count"] = friend.followers.count(), friend.following.count()
        return HttpResponse(json.dumps(result), content_type="application/json")
    except Exception as e:
        print(str(e))
        return redirect(reverse('user_login'))

def manage_post_likes(request, post_id):
    """ 
        This view handles post like/dislike from client against any post with post_id as args.
        ---- args ----
        post_id -> unique id of a post by an user

        RETURNS -> An HttpResponse sending a status update to the client whether the post was liked/disliked
    """
    try:
        if request.is_ajax():
            action = request.POST.get('action')
            try:
                post = PostModel.objects.filter(post_id=post_id).first()

                if action == 'liked':
                    action = "Liked the post!"
                else:
                    action = "Disliked the post!"

                if post.post_like_obj.filter(user=request.user).exists():
                    # Dislike post
                    post.post_like_obj.filter(user=request.user).delete()
                    del_notifications.delay(username=request.user.username, reaction="Disliked", send_to_username=post.user.username, post_id=post_id)
                    post.likes_count = F('likes_count') - 1
                    post.save()
                else:
                    # Like post
                    post.post_like_obj.add(PostLikes.objects.create(post_obj=post, user=request.user))
                    post.likes_count = F('likes_count') + 1
                    post.save()
                    # Notify the user whose post is being liked
                    send_notifications.delay(username=request.user.username, reaction="Liked", send_to_username=post.user.username, post_id=post_id)
            except Exception as e:
                print(str(e))
                return HttpResponse(json.dumps("post doesn't exist"), content_type="application/json")
        return HttpResponse(json.dumps({"status": "ready to update", "action":action}), content_type="application/json")
    except Exception as e:
        print(str(e))
        return redirect(reverse('user_login'))

def view_profile(request, username=None):
    try:
        """ 
            This view handles the profile page of any user.
            ---- args ----
            username -> user whose account profile page request.user wants to check out.
                        username will be = request.user.username if request.user is checking his/her own profile.
            
            RETURNS -> user data
        """
        try:
            user, editable = (request.user, True) if username == request.user.username else (User.objects.get(username=username), False)
        except ObjectDoesNotExist:
            return render(request, 'profile_500.html', {})

        current_user= Friends.objects.get(current_user=user)
        isFollower, isFollowing, isPending, follow_count, follower_count = None, None, None, 0, 0
        user_posts, saved_posts, user_posts_count = None, None, None
        show_private_msg = None
            
        # True if request.user follows the user he/she is searching for
        # True if request.user is in pending list of 'username'
        isPending = True if current_user.pending.filter(username=request.user).exists() else False
        if not isPending:
            isFollowing = True if current_user.followers.filter(username=request.user).exists() else False
            if not isFollowing:
                # True if request.user is being followed by 'username'
                isFollower = True if current_user.following.filter(username=request.user).exists() else False
            
        follow_count = current_user.following.count()
        follower_count = current_user.followers.count()
        user_posts_count = user.posts.count()

        # Get user account settings
        user_acc_settings = Account_Settings.objects.get(user=user)
        if user != request.user:
            # if account_settings of the user is set to Private, then request.user can only see user's photos or vidoes
            # iff isFollowing is True
            if user_acc_settings.private_acc:
                if isFollowing:
                    user_posts = user.posts.only('post_id', 'status_caption', 'pic_thumbnail', 'likes_count', 'comment_count')
                else:
                    # isFollowing -> False; User can see nothing! well, only followers,following & post count
                    user_posts, saved_posts = None, None
                    show_private_msg = "This account is private"
            else:   # account_settings of the user is set to Public
                user_posts = user.posts.only('post_id', 'status_caption', 'pic_thumbnail', 'likes_count', 'comment_count')
        else:
            # well, no restrictions for the user him/herself
            user_posts = user.posts.only('post_id', 'status_caption', 'pic_thumbnail', 'likes_count', 'comment_count')
            saved_posts = user.saved_by.only('post_id', 'status_caption', 'pic_thumbnail', 'likes_count', 'comment_count')

        if request.is_ajax():
            ajax_request = request.POST.get("activity")
            if ajax_request == 'get_user_acc_settings':
                # send current user account settings
                user_acc_settings = Account_Settings.objects.get(user=user)
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
        
        context = { 'profile':user, 'posts':user_posts, 'user_posts_count':user_posts_count, 
                    'saved_posts':saved_posts, 'editable':editable, 'isFollowing':isFollowing, 
                    'isFollower': isFollower, 'isPending':isPending, 'follow_count':follow_count, 
                    'follower_count':follower_count, 'private_msg':show_private_msg }

        return render(request, 'profile.html', context=context)
    except Exception as e:
        print(str(e))
        return redirect(reverse('user_login'))
    finally:
        close_old_connections()

def post_view(request, post_id):
    """
        This view handles post view page.
        ---- args ----
        post_id -> unique id of a post by an user

        RETURNS -> Post Data
    """
    try:
        post_obj = PostModel.objects.get_post(post_id=post_id)
        if post_obj is None:
            return render(request, 'post_500.html', {})
        else:
            if post_obj.user != request.user:
                post_user = post_obj.user
                if post_user.user_setting.private_acc:
                    # User who posted this has a private account
                    post_user_friend_obj = Friends.objects.get(current_user=post_user)
                    if request.user not in post_user_friend_obj.followers.all():
                        # User who posted this has a private account & request.user is not a follower of him/her
                        # Tresspassing?
                        return redirect(reverse('view_profile', kwargs={'username':post_user.username}))

        if request.is_ajax():
            try:
                post_obj = None
                if request.GET.get('activity') is not None:
                    # GET request, nothing needs to be updated
                    post_obj = PostModel.objects.get_post(post_id=post_id)
                else:
                    # POST request, post_obj needs to be updated
                    # Lock the rows of this obj till update is completed
                    with transaction.atomic():
                        post_obj = PostModel.objects.select_for_update().get(post_id=post_id)

                if request.GET.get('activity') == 'refresh comments':
                    post_comments, comment_count = post_obj.post_comment_obj.get_comments(request.user.username, post_obj)
                    editable = True if post_obj.user == request.user else False
                    post_comments_html = render_to_string("post_comments.html", {'comments':post_comments, 'editable':editable})
                    return HttpResponse(json.dumps({"post_comments_html":post_comments_html, "comment_count":comment_count}), content_type="application/json")
                if request.GET.get('activity') == 'refresh likes':
                    post_likes_list = post_obj.post_like_obj.select_related('user')
                    post_likes_html = render_to_string("post_likes.html", {"liked_user_list":post_likes_list})
                    return HttpResponse(json.dumps({"post_likes_html":post_likes_html, "likes_count":len(post_likes_list)}), content_type="application/json")
                if request.POST.get('activity') == 'add comment':
                    form = CommentForm(request.POST or None)
                    result = None
                    if form.is_valid():
                        reply = str(request.POST.get('reply'))
                        if "_" in reply:
                            index = reply.index("_")
                            comment_id, reply_id = reply[:index], reply[index+1:len(reply)]
                        else:
                            comment_id = reply
                            reply_id = None

                        if comment_id == '':
                            # request.user commented on a post with post_id=post_id
                            with transaction.atomic():
                                c = PostComments.objects.create(user=request.user, 
                                post_obj=post_obj, comment=form.cleaned_data.get('comment'))
                                post_obj.post_comment_obj.add(c)
                            send_notifications.delay(username=request.user.username, reaction='Commented', 
                            send_to_username=post_obj.user.username, post_id=post_id, comment_id=comment_id)
                        else:
                            # request.user replied to someone's comment on post with post_id=post_id
                            try:
                                with transaction.atomic():
                                    parent_comment = PostComments.objects.select_for_update().get(comment_id=comment_id)
                                    reply = form.cleaned_data.get('comment')
                                    c = PostComments.objects.create(user=request.user,
                                    post_obj=post_obj, comment=reply, parent=False)
                                    parent_comment.replies.add(c)
                                send_notifications.delay(username=request.user.username, reaction='Replied', 
                                send_to_username=reply_id, post_id=post_id, comment_id=c.comment_id)
                            except Exception as e:
                                print(str(e))
                                return None
                        with transaction.atomic():
                            post_obj.comment_count += 1
                            post_obj.save()
                        result = "ready to update"
                    else:
                        result = "save unsuccessful"
                    return HttpResponse(json.dumps(result), content_type='application/json')
                if request.POST.get('activity') == 'delete comment':
                    comment_id = str(request.POST.get('comment_id'))
                    try:
                        comment = PostComments.objects.get(comment_id=comment_id)
                        if comment.user == request.user or comment.post_obj == post_obj:
                            del_notifications.delay(reaction='Comment', notif_id=comment.comment_notif_id)
                            comment.delete()
                        # After comment_delete, send refreshed comments
                        post_comments, comment_count = post_obj.post_comment_obj.get_comments(request.user.username, post_obj)

                        with transaction.atomic():
                            # to ensure atomicity while updating values
                            post_obj.comment_count = comment_count
                            post_obj.save()

                        editable = True if post_obj.user == request.user else False
                        post_comments_html = render_to_string("post_comments.html", {'comments':post_comments, 'editable':editable})
                        return HttpResponse(json.dumps({"post_comments_html":post_comments_html, "comment_count":comment_count}), content_type="application/json")
                    except Exception as f:
                        print(f)
                        return HttpResponse(json.dumps("post_comment doesn't exist"), content_type="application/json")
                if request.POST.get('activity') == 'post bookmark':
                    if request.user in post_obj.saved_by.all():
                        post_obj.saved_by.remove(request.user)
                        return HttpResponse(json.dumps('Bookmark Removed!'), content_type="application/json")
                    else:
                        post_obj.saved_by.add(request.user)
                        return HttpResponse(json.dumps('Post Bookmarked!'), content_type="application/json")
            except Exception as e:
                print(str(e))
                return HttpResponse(json.dumps("post doesn't exist"), content_type="application/json")

        post_likes_list = post_obj.post_like_obj.select_related('user')
        post_comments, comment_count = post_obj.post_comment_obj.get_comments(request.user.username, post_obj)

        editable = True if post_obj.user == request.user else False
        
        liked_by_user = False
        if post_obj.post_like_obj.filter(user=request.user).exists():
            liked_by_user = True
        
        context = { 'user':request.user, 'post_data':post_obj, 'post_id': post_id, 
        'liked_user_list':post_likes_list, 'editable':editable, 
        'comments':post_comments, 'comment_count':comment_count,
        'liked_by_user':liked_by_user }

        return render(request, 'view_post.html', context=context)
    except Exception as e:
        print(str(e))
        return redirect(reverse('user_login'))

def del_user_post(request, post_id):
    """ 
        This view handles deletion of user posts iff a post with post_id sent through args is valid.
        ---- args ----
        post_id -> unique id of a post by an user

        RETURNS -> A redirect to view_profile
    """
    try:
        try:
            request.user.posts.get_post(post_id=post_id).delete()
        except ObjectDoesNotExist:
            pass
        return redirect(reverse('view_profile', kwargs={ 'username':request.user.username }))
    except Exception as e:
        print(str(e))
        return redirect(reverse('user_login'))

class edit_profile(TemplateView):
    """
        Self Explanatory. 
    """

    template_name = 'edit_profile.html'

    def get(self, request, username):
        try:
            edit_form = NonAdminChangeForm(instance=request.user)
            change_pass_form = CustomPasswordChangeForm(user=request.user)
            context = { 'edit_form':edit_form,'change_pass_form':change_pass_form }
            return render(request, self.template_name, context)
        except Exception as e:
            print(str(e))
            return redirect(reverse('user_login'))

    def post(self, request, username):
        try:
            result = {}
            prof_edited = False
            activity = request.POST.get('activity')
            # ------------ profile-edit request handling ------------
            if activity == 'validate_profile_data':
                edit_form = NonAdminChangeForm(request.POST or None, request.FILES or None, instance=request.user)
                if edit_form.is_valid():
                    prof_edited = True
                    if request.FILES:
                        old_prof_pic_path = None
                        user = User.get_user_obj(username=request.user.username)
                        if 'default' not in str(user.profile_pic):
                            old_prof_pic_path = str(user.profile_pic)

                        edit_form_model = edit_form.save(commit=False)
                        pic = Image.open(edit_form_model.profile_pic)
                        # create a BytesIO object
                        im_io = BytesIO()
                        # Compress image into thumbnail
                        size = (150, 150)
                        pic.thumbnail(size, Image.ANTIALIAS)
        
                        # save image to BytesIO object
                        # Now save the thumbnail into model's pic_thumbnail
                        # create a django-friendly Files object
                        if pic.format is 'PNG':
                            pic.save(im_io, format='PNG', quality=100, optimize=True)
                            edit_form_model.profile_pic = File(im_io, name=f"thumb_{str(edit_form_model.user_id)}.png")
                        else:
                            pic.save(im_io, format='JPEG', quality=95, optimize=True)
                            edit_form_model.profile_pic = File(im_io, name=f"thumb_{str(edit_form_model.user_id)}.jpg")
                        edit_form_model.save()
                    else:
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
                    if edit_form.has_error('profile_pic'):
                        result['profile_pic'] = edit_form.errors['profile_pic']
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
            
            if prof_edited:
                return HttpResponse(json.dumps({
                    'result':result, 'updated_username':request.user.username, 
                    'updated_prof_pic': str(request.user.profile_pic.url)}), content_type='application/json')
            return HttpResponse(json.dumps(result), content_type='application/json')
        except Exception as e:
            print(str(e))
            return redirect(reverse('user_login'))