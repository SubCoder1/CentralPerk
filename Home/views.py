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
        posts = PostModel.objects.values_list('status', 'location', 'user__username', 'user__profile_pic', named=True)

        args = { 'form':form, 'posts':posts }
        return render(request, self.template_name, context=args)
    
    def post(self, request):
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            return redirect('/home/')