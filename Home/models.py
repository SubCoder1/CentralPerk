from django.db import models
import uuid
from Profile.models import User
from datetime import datetime
import pytz
# Create your models here.
class PostModelManager(models.Manager):
    def get_post(self, post_id):
        return self.get(post_id=post_id)

    def get_liked_user_list(self, post_id):
        post = self.get_post(post_id)
        return post.likes.all()

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
    username = instance.user.username
    name = str(instance.unique_id)
    extension = filename[len(filename)-4:len(filename)]
    file_name = name + extension
    return f"post_images/user_{username}/{file_name}"

class PostModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, related_name='posts')
    send_to = models.ManyToManyField(User, related_name='connections', default=1)
    likes = models.ManyToManyField(User, related_name='likes', default=1)
    likes_count = models.PositiveIntegerField(default=0)
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.CharField(max_length=10, editable=False, default='')
    date_time = models.DateTimeField(blank=True)
    status_caption = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=200, blank=True)
    pic = models.ImageField(upload_to=user_directory_path, blank=True)
    objects = PostModelManager()

    class Meta:
        ordering = ('-date_time',)
        verbose_name = 'Post'

    def __str__(self):
        if self.status_caption and not self.pic:
            return 'status ' + self.post_id 
        else:
            return 'caption_pic ' + self.post_id

    def save(self, *args, **kwargs):
        return super(PostModel, self).save(*args, **kwargs)

REACTION = ( ('Liked', 'Liked'), ('Commented', 'Commented'), ('Sent Follow Request', 'Sent Follow Request'), )

class UserNotification(models.Model):
    user_to_notify = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, related_name='notifications', verbose_name="to_notify")
    # User who liked/commented 'to_notify's post or send him/her a follow request
    poked_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, blank=False, verbose_name="reacting_user")
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name="post", null=True, blank=True)
    date_time = models.DateTimeField(blank=True)
    reaction = models.CharField(max_length=20, choices=REACTION)
    objects = models.Manager()

    class Meta:
        ordering = ('-date_time',)

    @classmethod
    def create_notify_obj(cls, to_notify, by, reaction, date_time, post_obj=None):
        poked_user = User.objects.get(username=by)
        obj = cls.objects.create(user_to_notify=to_notify, poked_by=poked_user, post=post_obj, date_time=date_time, reaction=reaction)
        return obj

    def __str__(self):
        if self.post:
            if self.reaction == 'Liked':
                display = self.poked_by.username + " " + self.reaction + " " + self.user_to_notify.username + "'s " + self.post.post_id
            elif self.reaction == 'Commented':
                display = self.poked_by.username + " " + self.reaction + " on " + self.user_to_notify.username + "'s " + self.post.post_id
        else:
            display = self.poked_by.username + " " + self.reaction + " to " + self.user_to_notify.username
        
        return display