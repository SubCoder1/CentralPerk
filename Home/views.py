from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from Home.models import PostModel
from Home.forms import PostForm
from Profile.models import Friends
from Home.tasks import share_posts
from AUth.models import User
# Create your views here.

class home_view(TemplateView):
    template_name = 'index.html'

    def get(self, request):
        form = PostForm()
        posts = User.get_user_wall(username=request.user.username, is_namedtuple=True)

        args = { 'form':form, 'posts':posts }
        return render(request, self.template_name, context=args)

    def post(self, request):
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            post.send_to.add(request.user)
            share_posts.delay(request.user.username, post.post_id)   # Celery handling the task to share the post to user's followers
            return redirect('/home/')

def manage_likes(request, post_id):
    if PostModel.objects.likes_handler(request.user.username, post_id):
        return redirect('/home/')