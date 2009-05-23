from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from fivesongs.playlist.models import Playlist, Comment

class CommentForm(ModelForm):
    fullname = forms.CharField(label='Your Name', error_messages={'required': 'Please enter your name.'})
    email = forms.CharField(label='Your Email Address', error_messages={'required': 'Please enter a valid email address.'})
    website = forms.URLField(label='Your Web Site', required=False)
    body = forms.CharField(widget=forms.Textarea, error_messages={'required': 'Please enter a comment.'})

    class Meta:
        model = Comment

