from django import forms
from Home.models import PostModel, PostComments

class PostForm(forms.ModelForm):

    class Meta:
        model = PostModel
        fields = ('status_caption', 'pic', 'location')

class CommentForm(forms.ModelForm):

    class Meta:
        model = PostComments
        fields = ('comment',)