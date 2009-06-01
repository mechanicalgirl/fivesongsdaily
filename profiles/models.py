import datetime
import os.path
try:
    from PIL import Image, ImageFilter
except ImportError:
    import Image, ImageFilter

from django.db import models
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.files.storage import default_storage

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


class Avatar(models.Model):
    """
    """
    image = models.ImageField(upload_to="avatars/%Y/%b/%d", storage=default_storage)
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    valid = models.BooleanField()

    class Meta:
        unique_together = (('user', 'valid'),)

    def __unicode__(self):
        return _("%s's Avatar") % self.user

    def delete(self):
        if hasattr(settings, "AWS_SECRET_ACCESS_KEY"):
            path = urllib.unquote(self.image.name)
        else:
            path = self.image.path

        base, filename = os.path.split(path)
        name, extension = os.path.splitext(filename)
        for key in AVATAR_SIZES:
            try:
                storage.delete(os.path.join(base, "%s.%s%s" % (name, key, extension)))
            except:
                pass

        super(Avatar, self).delete()

    def save(self):
        for avatar in Avatar.objects.filter(user=self.user, valid=self.valid).exclude(id=self.id):
            if hasattr(settings, "AWS_SECRET_ACCESS_KEY"):
                path = urllib.unquote(self.image.name)
            else:
                path = avatar.image.path

            base, filename = os.path.split(path)
            name, extension = os.path.splitext(filename)
            for key in AVATAR_SIZES:
                try:
                    storage.delete(os.path.join(base, "%s.%s%s" % (name, key, extension)))
                except:
                    pass
            avatar.delete()

        super(Avatar, self).save()


