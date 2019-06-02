from django.contrib.auth.models import BaseUserManager

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