# Create your tasks here
from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from celery import shared_task
from Profile.models import Friends, User, Account_Settings
from Home.models import PostModel, UserNotification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def share_posts(username, post_id):
    try:
        post = PostModel.objects.get_post(post_id=post_id)
    except ObjectDoesNotExist:
        return "Task aborted, post not found(del?)"

    request_user = User.get_user_obj(username=username)
    following_list, created = Friends.objects.get_or_create(current_user=request_user)
    if not created:
        users = following_list.followers.all()
        channel_layer = get_channel_layer()
        if len(users) > 0:
            for user in users:
                post.send_to.add(user)
                if user.channel_name is not "":
                    async_to_sync(channel_layer.send)(user.channel_name, { "type" : "update.wall" })
            return "complete :)"
        else:
            return "user is lonely :("
    else:
        return "user is lonely :("

@shared_task
def send_notifications(username, reaction, send_to_username=None, post_id=None, private_request=None):
    # Check user account settings conditions before sending notifications
    send_to = User.get_user_obj(username=send_to_username)
    acc_settings = Account_Settings.objects.get(user=send_to)
    if acc_settings.disable_all:
        return 'User disabled all incoming notifications'
        
    if reaction == 'Liked' or reaction == 'Commented':
        if acc_settings.p_likes == 'Disable' and reaction == 'Liked' or reaction == 'Commented' and acc_settings.p_comments == 'Disable':
            return f'User disabled all incoming Post {reaction} Notifications'
        elif acc_settings.p_likes == 'From People I Follow' or acc_settings.p_comments == 'From People I Follow':
            relation_obj = Friends.objects.get(current_user=send_to)
            if not relation_obj.following.filter(username=username).exists():
                return f'User has set Post {reaction} notifications to following only'

    if reaction == 'Sent Follow Request':
        if acc_settings.f_requests:
            return 'User has disabled all incoming Follow Requests'

    if reaction == 'Commented' and acc_settings.p_comments == 'Disable':
        return 'User disabled all incoming Post Comments Notifications'
    
    # There's no restrictions on notifications set by send_to_user
    # Proceed with setting-up & sending notif to send_to_user
    channel_layer = get_channel_layer()
    if reaction == 'Liked' or reaction == 'Commented' or reaction == 'Replied':
        if send_to_username == username and reaction == 'Replied':
            return "User replied to his/her own comment :|"
        try:
            post = PostModel.objects.get_post(post_id=post_id)
        except ObjectDoesNotExist:
            return "Task aborted, post not found(del?)"
        
        if send_to_username == username and reaction == 'Replied':
            return "User replied to his/her own comment :|"
        
        if reaction != "Replied":
            send_to = post.user
            if send_to.username == username:
                return "User liked/commented on his/her own post :|"
        
        if UserNotification.create_notify_obj(to_notify=send_to, by=username, reaction=reaction, post_obj=post, private_request=False):
            if send_to.channel_name is not "":
                async_to_sync(channel_layer.send)(send_to.channel_name, { "type" : "send.updated.notif" })

        if reaction == 'Liked':
            return "like_notif sent successfully :)"
        elif reaction == 'Replied':
            return 'Reply_Notif sent successfully :)'
        else:
            return "comment_notif sent successfully :)"

    elif reaction == 'Sent Follow Request':
        UserNotification.create_notify_obj(to_notify=send_to, by=username, reaction=reaction, private_request=private_request)

        if send_to.channel_name is not "":
            async_to_sync(channel_layer.send)(send_to.channel_name, { "type" : "send.updated.notif" })

        return "follow_notif sent successfully :)"

@shared_task
def del_notifications(username, reaction, send_to_username=None, post_id=None):
    try:
        to_notify = User.objects.get(username=send_to_username)
        poked_by = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return "task aborted! No users found."
    
    query = None
    if reaction == 'Sent Follow Request':
        query = Q(user_to_notify=to_notify)
        query.add(Q(poked_by=poked_by), Q.AND)
        query.add(Q(reaction='Sent Follow Request'), Q.AND)
    elif reaction == 'Disliked':
        try:
            post = PostModel.objects.get(post_id=post_id)
        except ObjectDoesNotExist:
            return "Task aborted! No posts found(del by user?)"
        query = Q(user_to_notify=to_notify)
        query.add(Q(poked_by=poked_by), Q.AND)
        query.add(Q(reaction='Liked'), Q.AND)
        query.add(Q(post=post), Q.AND)

    if UserNotification.objects.filter(query).exists():
        UserNotification.objects.filter(query).first().delete()
        channel_layer = get_channel_layer()
        if to_notify.channel_name is not "":
            async_to_sync(channel_layer.send)(to_notify.channel_name, { "type" : "send.updated.notif" })
        return 'notif deleted successfully :)'
    else:
        return "filtered query doesn't exist.(Maybe user cleared his/her notif?)"       
        
