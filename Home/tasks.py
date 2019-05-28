# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from Profile.models import Friends
from django.contrib.auth import get_user_model
from Home.models import PostModel
from AUth.models import User

@shared_task
def share_posts(username, unique_id):
    request_user = User.objects.get(username=username)
    post = PostModel.objects.get(unique_id=unique_id)
    following_list, created = Friends.objects.get_or_create(current_user=request_user)
    if not created:
        users = following_list.followers.all()
        for user in users:
            post.send_to.add(user)
        return "complete :)"
    else:
        return "user is lonely :("