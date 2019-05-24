from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)

class UserManager(BaseUserManager):
    def create_user(self, username, full_name, birthdate, gender, email, bio, is_admin, is_staff, is_active, password=None):
        """Creates and saves a User with the given email and password. """

        if not email:
            raise ValueError("Users must have an Email address")
        if not password:
            raise ValueError("Users must have a password")
        if not username:
            raise ValueError("Users must have a username")
 
        email = self.normalize_email(email)
        user_obj = self.model(
            email=email, username=username, birthdate=birthdate, gender=gender, bio=bio,
            admin=is_admin, staff=is_staff, active=is_active, full_name=full_name
        )
        user_obj.set_password(password)
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, username, birthdate, gender, email, bio,password=None):
        """ Creates and saves a staff user with the given email and password. """

        user = self.create_user(
            email=email,
            username=username,
            full_name='',
            password=password,
            birthdate=birthdate,
            bio=bio,
            gender=gender,
            is_staff=True,
            is_admin=False,
            is_active=True,
        )
        return user

    def create_superuser(self, username, email, password=None):
        """ Creates and saves a super user with the given email and password. """

        user = self.create_user(
            username=username,
            full_name='',
            email=email,
            gender='Male',
            birthdate='',
            bio='',
            password=password,
            is_admin=True,
            is_staff=True,
            is_active=True,
        )
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=20,unique=True, primary_key=True)
    full_name = models.CharField(max_length=50)
    birthdate = models.CharField(max_length=10)
    bio = models.TextField(max_length=300)
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('other', 'other'),
    )
    gender = models.CharField(max_length=20, choices=GENDER)
    email = models.EmailField(max_length=255,unique=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    post_liked = models.ForeignKey('Home.PostModel', on_delete=models.DO_NOTHING, related_name='likes', null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
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