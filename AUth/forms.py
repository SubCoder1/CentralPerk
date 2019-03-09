from django import forms
from AUth.models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class Registerform(forms.ModelForm):
    """ A form for creating new users. Includes all the required fields """

    class Meta:
        model = User
        fields = ('username', 'email', 'gender', 'bio', 'password',)
    
    #--- for Validation ---

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'already exists!')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error('email', 'already exists!')
        return email

    def save(self,commit=True):
        user = super(Registerform, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.active = True
        user.admin  = False
        user.staff  = False
        if commit:
            user.save()
        return user

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