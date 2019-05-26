from django.db import models
import uuid
from AUth.models import User
from django.utils import timezone
import pytz
# Create your models here.

class PostModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='posts')
    send_to = models.ManyToManyField(User, related_name='connections', default=1)
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.CharField(max_length=10, editable=False, default='')
    date_time = models.DateTimeField(blank=True)
    status = models.CharField(max_length=500, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    pic = models.ImageField(upload_to='post_images', blank=True)
    objects = models.Manager()

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
        self.date_time = timezone.now().astimezone(tz)
        self.post_id = str(self.unique_id)[:8]
        return super(PostModel, self).save(*args, **kwargs)