from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.db.models import F, Prefetch
from django.db import close_old_connections
from django.urls import reverse
from django.contrib import messages
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from Home.models import PostModel, PostLikes, PostComments, UserNotification
from Home.forms import PostForm
from Profile.models import Friends, User
from Home.tasks import share_posts, send_notifications, del_notifications
from io import BytesIO
from datetime import datetime
import pytz, uuid, os
from PIL import Image
# Create your views here.

class home_view(TemplateView):
    template_name = 'index.html'

    def get(self, request):
        try:
            form = PostForm()
            posts = request.user.connections.prefetch_related(Prefetch('saved_by')).select_related('user')
            #notifications = request.user.notifications.select_related('poked_by', 'post')
            #followers, following = Friends.get_friends_list(current_user=request.user)

            args = { 'user':request.user, 'form':form, 'posts':posts, }
            return render(request, self.template_name, context=args)
        except Exception as e:
            print(str(e))
            return redirect(reverse('user_login'))
        finally:
            close_old_connections()

    def post(self, request):
        try:  
            form = PostForm(request.POST, request.FILES or None)
            if form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.post_id = str(post.unique_id)[:8]
                if post.pic:
                    pic = Image.open(post.pic)

                    if pic.format is not 'GIF':
                        # create a BytesIO object
                        im_io = BytesIO()
                        # Compress image into thumbnail
                        if pic.format is 'PNG':
                            pic = pic.convert('RGB')
                        
                        size = (300, 300)
                        pic.thumbnail(size, Image.ANTIALIAS)
                        # save image to BytesIO object
                        pic.save(im_io, format='JPEG', quality=95, optimize=True)
                        # Now save the thumbnail into model's pic_thumbnail
                        # create a django-friendly Files object
                        post.pic_thumbnail = File(im_io, name=f"thumb_{str(post.unique_id)}.jpg")
                post.save()
                
                post.send_to.add(request.user)
                # Celery handling the task to share the post to user's followers
                share_posts.delay(request.user.username, post.post_id)
                messages.success(request, 'Post Successful!')
            else:
                messages.error(request, 'Post Unsuccessful!')
            return redirect(reverse('home_view'))
        except Exception as e:
            print(str(e))
            return redirect(reverse('user_login'))
        finally:
            close_old_connections()