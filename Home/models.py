from django.db import models
from django.db.models import Prefetch
from django.db.models.signals import post_delete
from django.dispatch import receiver
import uuid, pytz
from Profile.models import User
from datetime import datetime
from collections import namedtuple
from hashlib import sha256
from random import getrandbits

# Create your models here.
class PostModelManager(models.Manager):
    def get_post(self, post_id):
        return self.filter(post_id=post_id).select_related('user').first()

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
    user_id = instance.user.user_id
    name = str(instance.unique_id)
    extension = filename[len(filename)-4:len(filename)]
    file_name = name + extension
    return f"post_images/{user_id}/{file_name}"

class PostModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, related_name='posts')
    send_to = models.ManyToManyField(User, related_name='connections', default=1)
    saved_by = models.ManyToManyField(User, related_name='saved_by', default=1)
    likes_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.CharField(max_length=10, editable=False, default='', db_index=True)
    date_time = models.DateTimeField(auto_now_add=True)
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

@receiver(post_delete, sender=PostModel)
def submission_delete(sender, instance, **kwargs):
    instance.pic.delete(False)

class PostLikes(models.Model):
    post_obj = models.ForeignKey(PostModel, on_delete=models.CASCADE, default=1, related_name='post_like_obj')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='liked_by')
    date_time = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Post_Like'

    def __str__(self):
        return str(self.post_obj)

class PostCommentsManager(models.Manager):
    def parent(self):
        qs = super(PostCommentsManager, self).filter(parent=True)
        return qs

    def get_comments(self, post):
            #post = PostModel.objects.get_post(post_id=post_id)
            qs = []
            layout = namedtuple("comment", ["profile_pic", "username", "comment", "comment_id", "date_time", "reply"])
            parent_comment_qs = post.post_comment_obj.parent().select_related('user')
            comments = parent_comment_qs.prefetch_related(Prefetch('replies',queryset=PostComments.objects.select_related('user')))
            count = 0
            for parent_comment in comments:
                count += 1
                prof_pic = parent_comment.user.profile_pic.url
                username = parent_comment.user.username
                comment = parent_comment.comment
                c_id = parent_comment.comment_id
                date_time = parent_comment.date_time
                replies = []

                for reply in parent_comment.replies.all():
                    count += 1
                    reply_prof_pic = reply.user.profile_pic.url
                    reply_username = reply.user.username
                    reply_comment = reply.comment
                    reply_id = reply.comment_id
                    reply_dt = reply.date_time
                    replies.append(layout(profile_pic=reply_prof_pic, username=reply_username, comment=reply_comment, 
                    comment_id=reply_id, date_time=reply_dt, reply=None))
                
                qs.append(layout(profile_pic=prof_pic, username=username, comment=comment, comment_id=c_id, 
                date_time=date_time, reply=replies))
            
            return (qs, count)

    def create(self, user, post_obj, comment, parent=True, reply=None):
        comment_id = str(uuid.uuid4())[:8]
        comment_obj = super(PostCommentsManager, self).create(user=user, post_obj=post_obj, comment_id=comment_id, comment=comment, parent=parent, reply=reply)
        comment_obj.save()
        return comment_obj

class PostComments(models.Model):
    comment_id = models.CharField(primary_key=True, max_length=10, editable=False, default='')
    post_obj = models.ForeignKey(PostModel, on_delete=models.CASCADE, default=1, related_name='post_comment_obj')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='comment_by')
    comment = models.TextField(blank=False)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    date_time = models.DateTimeField(auto_now_add=True)
    parent = models.BooleanField(default=True)
    objects = PostCommentsManager()

    class Meta:
        verbose_name = 'Post_Comment'
        ordering = ('date_time',)

    def __str__(self):
        return self.comment_id

    @property
    def has_replies(self):
        if self.reply is not None:
            return True
        return False

REACTION = (('Liked', 'Liked'), ('Commented', 'Commented'), ('Mentioned', 'Mentioned'),
            ('Sent Follow Request', 'Sent Follow Request'), ('Replied', 'Replied'),)

class UserNotification(models.Model):
    notif_id = models.CharField(default='', max_length=65, blank=True, null=True)
    user_to_notify = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='notifications', verbose_name="to_notify")
    private_request = models.BooleanField(default=False, null=True)
    private_request_id = models.CharField(max_length=100, blank=True, null=True)
    # User who liked/commented 'user_to_notify's post or send him/her a follow request
    poked_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, blank=False, verbose_name="reacting_user")
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name="post", null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    reaction = models.CharField(max_length=20, choices=REACTION)
    objects = models.Manager()

    class Meta:
        ordering = ('-date_time',)

    def __str__(self):
        return str(self.poked_by) + " --> " + str(self.user_to_notify) + " " + str(self.reaction)

    @classmethod
    def create_notify_obj(cls, to_notify, by, reaction, post_obj=None, private_request=False):
        poked_user = User.get_user_obj(username=by)
        obj = cls.objects.create(user_to_notify=to_notify, private_request=private_request, poked_by=poked_user, post=post_obj, reaction=reaction)
        obj.notif_id = getrandbits(64)
        if private_request:
            request_id = str(to_notify.user_id) + str(obj.notif_id)
            request_id_hash = sha256(bytes(request_id, encoding='utf-8'))
            obj.private_request_id = request_id_hash.hexdigest()
        obj.save()
        return obj