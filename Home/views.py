from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.db.models import F
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from Home.models import PostModel, PostLikes, PostComments, UserNotification
from Home.forms import PostForm
from Profile.models import Friends, User
from Home.tasks import share_posts, send_notifications, del_notifications
from datetime import datetime
import pytz, uuid
# Create your views here.

class home_view(TemplateView):
    template_name = 'index.html'

    def get(self, request):
        form = PostForm()
        posts = request.user.connections.values_list(
            'status_caption', 'pic',
            'location', 'user__username', 'user__profile_pic',
            'date_time', 'likes_count', 'comment_count', 'post_id', named=True)
        notifications = request.user.notifications.values_list(
            'poked_by__username', 'date_time', 'reaction', 'poked_by__profile_pic', named=True)
        online_users, followers, following = Friends.get_friends_list(current_user=request.user)

        args = { 'form':form, 'posts':posts, 'notifications':notifications,
                 'online_users':online_users, 'followers':followers, 'following':following }
        return render(request, self.template_name, context=args)

    def post(self, request):
        form = PostForm(request.POST, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.post_id = str(post.unique_id)[:8]
            post.save()
            post.send_to.add(request.user)
            share_posts.delay(request.user.username, post.post_id)  # Celery handling the task to share the post to user's followers
            messages.success(request, 'Post Successful!')
        else:
            messages.error(request, 'Post Unsuccessful!')
            return redirect(reverse('home_view'))
        return redirect(reverse('home_view'))

def clear_all_notification(request):
    request.user.notifications.all().delete()
    return redirect(reverse('home_view'))