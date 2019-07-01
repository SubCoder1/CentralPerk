from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from Profile.user_manager import UserManager
# Create your models here.

GENDER = ( ('Male', 'Male'), ('Female', 'Female'), ('other', 'other'), )

class User(AbstractBaseUser):
    session_key = models.CharField(max_length=40, default='notyetaccquired')
    username = models.CharField(max_length=20,unique=True, primary_key=True)
    full_name = models.CharField(max_length=50)
    birthdate = models.CharField(max_length=10)
    bio = models.TextField(max_length=300)
    gender = models.CharField(max_length=20, choices=GENDER)
    email = models.EmailField(max_length=255,unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    profile_pic = models.ImageField(upload_to='profile_pics', default='/profile_pics/default.png')
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