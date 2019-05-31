from django.db import models
import uuid
from AUth.models import User
from datetime import datetime
import pytz
# Create your models here.
class PostModelManager(models.Manager):
    def get_post(self, post_id):
        return self.get(post_id=post_id)

    def get_liked_user_list(self, post_id):
        post = self.get_post(post_id)
        return post.likes.all()
    
    def likes_handler(self, username, post_id):
        user = User.objects.get(username=username)
        post = self.get_post(post_id)
        if user in post:
            # Dislike post
            post.likes_count -= 1
            post.likes.remove(user)
        else:
            # Like post
            post.likes_count += 1
            post.likes.add(user)
        
        post.save()
        return "handled :)"

class PostModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, related_name='posts')
    send_to = models.ManyToManyField(User, related_name='connections', default=1)
    likes = models.ManyToManyField(User, related_name='likes', default=1)
    likes_count = models.PositiveIntegerField(default=0)
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.CharField(max_length=10, editable=False, default='')
    date_time = models.DateTimeField(blank=True)
    status = models.CharField(max_length=500, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    pic = models.ImageField(upload_to='post_images', blank=True)
    objects = PostModelManager()

    class Meta:
        ordering = ('-date_time',)
        verbose_name = 'Post'

    def __str__(self):
        if self.status:
            return 'status ' + self.post_id 
        else:
            return 'pic ' + self.post_id

    def save(self, *args, **kwargs):
        ''' On save, update post date_time '''
        tz = pytz.timezone('Asia/Kolkata')
        self.date_time = datetime.now().astimezone(tz)
        self.post_id = str(self.unique_id)[:8]
        return super(PostModel, self).save(*args, **kwargs)