from django import forms
from Home.models import PostModel

class PostForm(forms.ModelForm):

    class Meta:
        model = PostModel
        fields = ('status','location')