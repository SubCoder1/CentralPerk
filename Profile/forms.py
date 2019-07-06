from django import forms
from Profile.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField

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
        fields = ('username', 'birthdate', 'gender', 'bio', 'email',)
    
    #--- for Validation ---

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists() and self.instance.username != username:
            self.add_error('username', 'already exists!')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() and self.instance.email != email:
            self.add_error('email', 'already exists!')
        return email