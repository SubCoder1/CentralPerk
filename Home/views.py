from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from Home.models import PostModel
from Home.forms import PostForm
from Profile.models import Friends
import datetime
from Home.tasks import share_posts
from django.core.serializers import serialize
# Create your views here.

class home_view(TemplateView):
    template_name = 'index.html'

    def get(self, request):
        form = PostForm()
        #posts = PostModel.objects.values_list('status', 'location', 'user__username', 'user__profile_pic', 'date_time', named=True)
        posts = request.user.connections.all().values_list(
            'status', 'caption', 'pic', 
            'location', 'user__username', 'user__profile_pic', 
            'date_time', 'likes_count', named=True)

        args = { 'form':form, 'posts':posts }
        return render(request, self.template_name, context=args)
    
    def post(self, request):
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            post.send_to.add(request.user)
            share_posts.delay(request.user.username, post.unique_id)   # Celery handling the task to share the post to user's followers
            return redirect('/home/')