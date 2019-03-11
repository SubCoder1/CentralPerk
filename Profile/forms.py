from django import forms
from AUth.models import User

class NonAdminChangeForm(forms.ModelForm):
    """ A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field. """
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