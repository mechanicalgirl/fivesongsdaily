from django.db import models
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    user contact data, photo, personal information, etc.
    A basic profile which stores user information after the account has been activated.
    Use this model as the value of the ``AUTH_PROFILE_MODULE`` setting
    """
    user = models.ForeignKey(User, editable=False)
    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.IntegerField(max_length=5, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True)
    livejournal = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=100, blank=True)
    favorite_bands = models.TextField("Favorite bands", blank=True)
    email_notify = models.BooleanField(default=False)
    visible = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def fullname(self):
        return "%s, %s" %(self.last_name,self.first_name)
        fullname.short_description = 'Full Name'

    class Meta:
        ordering = ['last_name']



