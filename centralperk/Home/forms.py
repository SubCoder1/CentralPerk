from django import forms
from django.core.exceptions import ValidationError
from Home.models import PostModel, PostComments

class PostForm(forms.ModelForm):

    class Meta:
        model = PostModel
        fields = ('status_caption', 'pic', 'location')
    
    def clean(self):
        status_caption = str(self.cleaned_data.get('status_caption'))
        if status_caption.isspace() or len(status_caption) < 1: # status_caption field is empty
            if not self.cleaned_data.get('pic'):    # No pic uploaded
                # No pic uploaded + no status means empty post... Throw an error
                self.add_error('status_caption', 'cannot be empty')
                self.add_error('pic', 'cannot be blank')

        return self.cleaned_data

class CommentForm(forms.ModelForm):

    class Meta:
        model = PostComments
        fields = ('comment',)
    
    def clean_comment(self):
        comment = str(self.cleaned_data.get('comment'))
        if comment.isspace() or not len(comment):
            # Cannot accept blank comments or comments with only spaces or newlines
            self.add_error('comment', 'cannot be empty')
        return comment