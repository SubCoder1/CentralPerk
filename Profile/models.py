from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_delete
from django.dispatch import receiver
from Profile.user_manager import UserManager
import uuid
# Create your models here.

GENDER = ( ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'), )

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<user_id>/<filename>
    return f"profile_pics/{instance.user_id}/{filename}"

class User(AbstractBaseUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40, default='notyetaccquired')
    channel_name = models.CharField(max_length=100, default="", blank=True, null=True)
    username = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=50)
    birthdate = models.CharField(max_length=10)
    bio = models.TextField(max_length=160,  default="I am breathtaking!", blank=True)
    gender = models.CharField(max_length=20, choices=GENDER)
    email = models.EmailField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    profile_pic = models.ImageField(upload_to=user_directory_path, default='/profile_pics/default.png')
    admin = models.BooleanField(default=False) # a superuser
    staff = models.BooleanField(default=False) # a admin user; non super-user
    active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]

    def __str__(self):
        return self.username

    def is_staff(self):
        return self.staff

    def is_admin(self):
        return self.admin
    
    def is_active(self):
        return self.active

    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True

    objects = UserManager()
    
    @classmethod
    def get_user_obj(cls, username):
        return cls.objects.get(username=username)

@receiver(post_delete, sender=User)
def submission_delete(sender, instance, **kwargs):
    instance.pic.delete(False)

POST_NOTIF_CHOICES = (('Disable', 'Disable'), ('From People I Follow', 'From People I Follow'), ('From Everyone', 'From Everyone'))
class Account_Notif_Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    disable_all = models.BooleanField(default=False)
    p_likes = models.CharField(verbose_name='Post Likes', max_length=21, choices=POST_NOTIF_CHOICES, default=POST_NOTIF_CHOICES[2][1])
    p_comments = models.CharField(verbose_name='Post Comments', max_length=21, choices=POST_NOTIF_CHOICES, default=POST_NOTIF_CHOICES[2][1])
    p_comment_likes = models.CharField(verbose_name='Post Comment Likes', max_length=21, choices=POST_NOTIF_CHOICES, default=POST_NOTIF_CHOICES[0][1])
    f_requests = models.BooleanField(default=False)
    private_acc = models.BooleanField(default=False, null=True)
    activity_status = models.BooleanField(default=True, null=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "User Setting"

    def __str__(self):
        return str(self.user)

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

    @classmethod
    def get_friends_list(cls, current_user):
        friend_obj, created = cls.objects.get_or_create(current_user=current_user)
        online_friends, followers, following = None, None, None
        if not created:
            online_friends = friend_obj.following.filter(active=True).values_list('username', 'profile_pic', named=True)
            followers = friend_obj.followers.values_list('username', 'profile_pic', named=True)
            following = friend_obj.following.values_list('username', 'profile_pic', 'last_login', 'active', named=True)
        return (online_friends, followers, following)

    class Meta:
        verbose_name = 'Relation'