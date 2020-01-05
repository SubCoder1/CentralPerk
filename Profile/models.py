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
    monitor_task_id = models.CharField(max_length=60, default="", blank=True, null=True)
    channel_name = models.CharField(max_length=100, default="", blank=True, null=True)
    username = models.CharField(max_length=20, default='',unique=True)
    full_name = models.CharField(max_length=50)
    birthdate = models.CharField(max_length=10)
    bio = models.TextField(max_length=160,  default="I am breathtaking!", blank=True)
    gender = models.CharField(max_length=20, choices=GENDER)
    email = models.EmailField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    just_created = models.BooleanField(default=True)
    profile_pic = models.ImageField(blank=True, upload_to=user_directory_path)
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
    instance.profile_pic.delete(False)

POST_NOTIF_CHOICES = (('Disable', 'Disable'), ('From People I Follow', 'From People I Follow'), ('From Everyone', 'From Everyone'))
class Account_Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_setting")
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
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_user')
    followers = models.ManyToManyField(User)
    pending = models.ManyToManyField(User, related_name='pending_requests')
    following = models.ManyToManyField(User, related_name='following')
    objects = models.Manager()

    @classmethod
    def follow(cls, current_user, follow_user):
        # current_user -> following +1
        friend = cls.objects.get(current_user=current_user)
        friend.following.add(follow_user)
        
        # follow_user -> follow +1
        friend= cls.objects.get(current_user=follow_user)
        friend.followers.add(current_user)

    @classmethod
    def unfollow(cls, current_user, unfollow_user):
        # current_user -> following -1
        friend= cls.objects.get(current_user=current_user)
        friend.following.remove(unfollow_user)

        #unfollow_user -> follow -1
        friend = cls.objects.get(current_user=unfollow_user)
        friend.followers.remove(current_user)

    @classmethod
    def add_to_pending(cls, current_user, pending_user):
        # add the current_user to pending_user's pending list.
        friend = cls.objects.get(current_user=pending_user)
        friend.pending.add(current_user)

    @classmethod
    def rm_from_pending(cls, current_user, pending_user):
        # remove the current_user from pending_user's pending list.
        # This function is called when the current_user wants to cancel any friend request sent to pending_user.
        # (Private Account)
        friend = cls.objects.get(current_user=current_user)
        friend.pending.remove(pending_user)

    @classmethod
    def get_friends_list(cls, current_user):
        friend_obj, created = cls.objects.get_or_create(current_user=current_user)
        online_friends, followers, following = None, None, None
        if not created:
            #online_friends = friend_obj.following.filter(active=True, user_setting__activity_status=True).only('username', 'full_name', 'profile_pic')
            followers = friend_obj.followers.only('username', 'full_name', 'profile_pic')
            following = friend_obj.following.filter(user_setting__activity_status=True).only('username', 'profile_pic', 'full_name', 'last_login', 'active')
        return (followers, following)

    class Meta:
        verbose_name = 'Relation'