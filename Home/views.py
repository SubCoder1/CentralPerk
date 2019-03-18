from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from Home.models import PostModel
from Home.forms import PostForm
import datetime
# Create your views here.

class home_view(TemplateView):
    template_name='index.html'

    def get(self, request):
        form = PostForm()
        posts = PostModel.objects.all()

        args = { 'form':form, 'posts':posts }
        return render(request, self.template_name, context=args)
    
    def post(self, request):
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.post_id = str(post.unique_id)[:8]
            post.date_time = datetime.datetime.now()
            post.user = request.user
            post.save()

            return redirect('/home/')