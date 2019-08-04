from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from Profile.models import User, Account_Notif_Settings
from Home.tasks import send_notifications, del_notifications
from Home.models import PostModel, PostLikes

@shared_task
def update_user_acc_settings(username, data):
    try:
        user = User.get_user_obj(username=username)
        user_acc_settings = Account_Notif_Settings.objects.get(user=user)
        post_choices = ('Disable', 'From People I Follow', 'From Everyone')
        if data.get('disable_all') == 'true':
            user_acc_settings.disable_all = True
        else:
            user_acc_settings.disable_all = False
        if data.get('p_likes') in post_choices:
            user_acc_settings.p_likes = data['p_likes']
        if data.get('p_comments') in post_choices:
            user_acc_settings.p_comments = data['p_comments']
        if data.get('p_comment_likes') in post_choices:
            user_acc_settings.p_comment_likes = data['p_comment_likes']
        if data.get('f_requests') == 'true':
            user_acc_settings.f_requests = True
        else:
            user_acc_settings.f_requests = False
        user_acc_settings.save()

        return f"User - {user.username}'s account was successfully updated."
    except ObjectDoesNotExist:
        return 'User object not found'
    except:
        return 'User account settings was not successfully updated :('

@shared_task
def manage_likes(post_id, username):
    try:
        post = PostModel.objects.get_post(post_id=post_id)
        user = User.get_user_obj(username=username)
        if post.post_like_obj.filter(user=user).exists():
            # Dislike post
            post.post_like_obj.filter(user=user).delete()
            del_notifications.delay(username=user.username, reaction="Disliked", send_to_username=post.user.username, post_id=post_id)
            post.likes_count = F('likes_count') - 1
            post.save()
            return f'post - {post_id} was disliked by {username}'
        else:
            # Like post
            post.post_like_obj.add(PostLikes.objects.create(post_obj=post, user=user))
            post.likes_count = F('likes_count') + 1
            post.save()
            # Notify the user whose post is being liked
            send_notifications.delay(username=user.username, reaction="Liked", send_to_username=post.user.username, post_id=post_id)
            return f'post - {post_id} was liked by {username}'
    except:
        return 'task failed'