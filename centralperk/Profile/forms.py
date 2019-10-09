from django import forms
from Profile.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField, PasswordChangeForm
from AUth.tasks import (
check_username_validity, check_email_validity, 
check_fullname_validity, check_pass_strength
)
from datetime import datetime
from PIL import Image

class UserAdminChangeForm(forms.ModelForm):
    """ A form for updating (Admin) users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field. """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'birthdate', 'gender', 'email', 'bio', 'password',)
 
    def clean_password(self):
        return self.initial["password"]

class NonAdminChangeForm(forms.ModelForm):
    """ A form used to edit (non-admin) user profiles """
    class Meta:
        model = User
        fields = ('profile_pic', 'username', 'full_name', 'email', 'birthdate', 'gender', 'bio',)

    #--- for Validation ---

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic', None)
        if profile_pic is not None:
            img = Image.open(profile_pic)
            img_mime = Image.MIME[img.format]
            #print(img_mime)
            # Profile_pic cannot be a GIF or of any other type than those listed below
            if str(img_mime) not in ['image/jpg', 'image/png', 'image/jpeg']:
                self.add_error('profile_pic', 'Invalid image type')
        return profile_pic

    def clean_username(self):
        username = self.cleaned_data['username']
        if username != self.instance.username:
            status = check_username_validity.delay(username).get()
            if status != 'valid username':
                self.add_error('username', status)
        return username

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if len(full_name) > 1 and full_name != self.instance.full_name:
            status = check_fullname_validity.delay(full_name).get()
            if status != 'valid fullname':
                self.add_error('full_name', status)
        return full_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if email != self.instance.email:
            if not len(email):
                self.add_error('email', 'Email cannot be empty')
            else:
                status = check_email_validity.delay(email).get()
                if status != 'valid email':
                    self.add_error('email', status)
        return email

    def clean_birthdate(self):
        birthdate = str(self.cleaned_data['birthdate'])
        try:
            correct_format = "%d-%m-%Y"
            datetime.strptime(birthdate, correct_format)
            return birthdate
        except:
            self.add_error('birthdate', 'Incorrect format')

    def clean_gender(self):
        gender = self.cleaned_data['gender']
        choices = ['Male', 'Female', 'Other']
        if gender not in choices:
            self.add_error('gender', 'You have to choose one')
        return gender

    def clean_bio(self):
        bio = self.cleaned_data['bio']
        if len(bio) > 300:
            self.add_error('bio', 'Bio should be less than 300 characters')
        return bio

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        email = self.user.email
        username = self.user.username
        new_password1 = self.cleaned_data['new_password1']
        status = check_pass_strength.delay(new_password1, username, email).get()
        if status != 'strong password':
            self.add_error('new_password1', status)
        return new_password1