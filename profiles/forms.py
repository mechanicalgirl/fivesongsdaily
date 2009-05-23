from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from fivesongs.profiles.models import UserProfile
from fivesongs.profiles.data.choices import states, countries

class UserProfileForm(ModelForm):
    state = forms.ChoiceField(label='State', widget=forms.Select(attrs={'class':'input_select'}), choices=states, required=False)
    country = forms.ChoiceField(label='Country', widget=forms.Select(attrs={'class':'input_select'}), choices=countries, required=False)

    class Meta:
        model = UserProfile
        exclude = ('user',)



