from django import forms
from Profile.models import User
from AUth.tasks import check_username_validity, check_email_validity, check_pass_strength

class Registerform(forms.ModelForm):
    """ A form for creating new users. Includes all the required fields """

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'gender', 'password',)
    
    #--- for Validation ---

    def clean_username(self):
        username = self.cleaned_data['username']
        status = check_username_validity.delay(username).get()
        if status != 'valid username':
            self.add_error('username', status)
        return username

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']
        if len(full_name) > 50:
            self.add_error('full_name', 'Full name should be < 51 characters')
        return full_name

    def clean_email(self):
        email = self.cleaned_data['email']
        status = check_email_validity.delay(email).get()
        if status != 'valid email':
            self.add_error('email', status)
        return email

    def clean_gender(self):
        gender = self.cleaned_data['gender']
        choices = ['Male', 'Female', 'Other']
        if gender not in choices:
            self.add_error('gender', 'You have to choose one')
        return gender

    def clean_password(self):
        password = self.cleaned_data['password']
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        status = check_pass_strength.delay(password, username, email).get()
        if status != 'strong password':
            self.add_error('password', status)
        return password

    def save(self,commit=True):
        user = super(Registerform, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.active = True
        user.admin  = False
        user.staff  = False
        if commit:
            user.save()
        return user