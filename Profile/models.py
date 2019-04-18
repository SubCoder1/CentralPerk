from django.db import models
from AUth.models import User
# Create your models here.
class Friends(models.Model):
    followers = models.ManyToManyField(User)
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_user')
    following = models.ManyToManyField(User, related_name='following')
    objects = models.Manager()

    @classmethod
    def follow(cls, current_user, follow_user):
        # current_user -> following +1
        friend, created = cls.objects.get_or_create(current_user=current_user)
        del created
        friend.following.add(follow_user)
        
        # follow_user -> follow +1
        friend, created = cls.objects.get_or_create(current_user=follow_user)
        del created
        friend.followers.add(current_user)


    @classmethod
    def unfollow(cls, current_user, unfollow_user):
        # current_user -> following -1
        friend, created = cls.objects.get_or_create(current_user=current_user)
        del created
        friend.following.remove(unfollow_user)

        #unfollow_user -> follow -1
        friend, created = cls.objects.get_or_create(current_user=unfollow_user)
        del created
        friend.followers.remove(current_user)

    class Meta:
        verbose_name = 'Friend'