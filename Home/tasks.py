# Create your tasks here
from __future__ import absolute_import, unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from Profile.models import Friends, User
from django.contrib.auth import get_user_model
from Home.models import PostModel, UserNotification
from datetime import datetime
import pytz

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
        if len(users) > 0:
            for user in users:
                post.send_to.add(user)
            return "complete :)"
        else:
            return "user is lonely :("
    else:
        return "user is lonely :("

@shared_task
def send_notifications(username, reaction, send_to_username=None, post_id=None):
    if reaction == 'Liked' or reaction == 'Commented':
        try:
            post = PostModel.objects.get_post(post_id=post_id)
        except ObjectDoesNotExist:
            return "Task aborted, post not found(del?)"
 
        send_to = post.user
        if send_to.username == username:
            return "User liked/commented_on his/her own post :|"
        

        if UserNotification.create_notify_obj(to_notify=send_to, by=username, reaction=reaction, post_obj=post):
            if reaction == 'Liked':
                return "like_notif sent successfully :)"
            else:
                return "comment_notif sent successfully :)"

    elif reaction == 'Sent Follow Request' or reaction == 'Replied':
        send_to = User.get_user_obj(username=send_to_username)
        if send_to.username == send_to_username and reaction == 'Replied':
            return "User replied his/her own comment :|"
        if UserNotification.create_notify_obj(to_notify=send_to, by=username, reaction=reaction):
            if reaction == 'Sent Follow Request':
                return "follow_notif sent successfully :)"
            else:
                return "reply_notif sent successfully :)"