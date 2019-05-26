from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from Home.models import PostModel
from Home.forms import PostForm
from Profile.models import Friends
import datetime
# Create your views here.

class home_view(TemplateView):
    template_name = 'index.html'

    def get(self, request):
        form = PostForm()
        #posts = PostModel.objects.values_list('status', 'location', 'user__username', 'user__profile_pic', 'date_time', named=True)
        posts = request.user.connections.all().values_list('status', 'location', 'user__username', 'user__profile_pic', 'date_time', named=True)

        args = { 'form':form, 'posts':posts }
        return render(request, self.template_name, context=args)
    
    def post(self, request):
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            post.send_to.add(request.user)
            following_list, created = Friends.objects.get_or_create(current_user=request.user)
            if not created:
                users = following_list.followers.all()
                for user in users:
                    post.send_to.add(user)

            return redirect('/home/')