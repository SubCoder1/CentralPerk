from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from Home.models import PostModel, UserNotification
from Home.forms import PostForm
from Profile.models import Friends, User
from Home.tasks import share_posts, send_notifications
from datetime import datetime
import pytz
# Create your views here.

class home_view(TemplateView):
    template_name = 'index.html'

    def get(self, request):
        form = PostForm()
        posts = request.user.connections.all().values_list(
            'status', 'caption', 'pic', 
            'location', 'user__username', 'user__profile_pic', 
            'date_time', 'likes_count', 'post_id', named=True)
        notifications = request.user.notifications.all().values_list(
            'poked_by', 'date_time', 'reaction', 'poked_by__profile_pic',named=True)

        args = { 'form':form, 'posts':posts, 'notifications':notifications }
        return render(request, self.template_name, context=args)

    def post(self, request):
        form = PostForm(request.POST or None)
        tz = pytz.timezone('Asia/Kolkata')
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.post_id = str(post.unique_id)[:8]
            post.date_time = datetime.now().astimezone(tz)
            post.save()
            post.send_to.add(request.user)
            share_posts.delay(request.user.username, post.post_id)  # Celery handling the task to share the post to user's followers
            return redirect('/home/')

def clear_all_notification(request):
    request.user.notifications.all().delete()
    return redirect('/home/')

def manage_home_post_likes(request, post_id):
    try:
        post = PostModel.objects.get_post(post_id=post_id)
    except ObjectDoesNotExist:
        return render(request, 'post_500.html', {})

    user = request.user
    if user in post.likes.all():
        # Dislike post
        post.likes.remove(user)
        post.likes_count = F('likes_count') - 1
        post.save()
    else:
        # Like post
        post.likes.add(user)
        post.likes_count = F('likes_count') + 1
        post.save()

        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now().astimezone(tz)
        # Notify the user whose post is being liked
        send_notifications.delay(username=request.user.username, reaction="Liked", date_time=now, post_id=post_id)

    return redirect('/home/')