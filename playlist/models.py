import logging

from django.db import models
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class Song(models.Model):
    """
    """
    user = models.ForeignKey(User, editable=True)
    artist = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True)
    filepath = models.FileField('file upload', upload_to='mp3/', blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u"%s - %s" %(self.artist, self.title)

    class Meta:
        ordering = ['-created_at']
	unique_together = ("artist", "title",)

class Playlist(models.Model):
    """
    """
    user = models.ForeignKey(User, editable=True)
    play_date = models.DateField()
    song1 = models.ForeignKey(Song, related_name="song1")
    song2 = models.ForeignKey(Song, related_name="song2")
    song3 = models.ForeignKey(Song, related_name="song3")
    song4 = models.ForeignKey(Song, related_name="song4")
    song5 = models.ForeignKey(Song, related_name="song5")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u"%s" % self.play_date

    def get_absolute_url(self):
        return "/playlist/%s/" % self.id
        # maybe make this by date?

    class Meta:
        ordering = ['-play_date']
	unique_together = ("song1", "song2", "song3", "song4", "song5",)

class Comment(models.Model):
    """
    """
    post = models.ForeignKey(Playlist)
    fullname = models.CharField(max_length=60)
    email = models.CharField(max_length=60)
    website = models.URLField(verify_exists=True, max_length=255, blank=True)
    body = models.TextField()
    publish = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u"%s" % self.id

    class Meta:
        ordering = ['-created_at']

    # custom method to clean website - make sure it's a complete url

from django.contrib.comments.signals import comment_was_posted

def on_comment_was_posted(sender, comment, request, *args, **kwargs):
    # spam checking can be enabled/disabled per the comment's target Model
    #if comment.content_type.model_class() != Entry:
    #    return

    from django.contrib.sites.models import Site
    from django.conf import settings

    try:
        from akismet import Akismet
    except:
        return

    ak = Akismet(
        key=settings.AKISMET_API_KEY,
        blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain
    )

    if ak.verify_key():
        data = {
            'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referrer': request.META.get('HTTP_REFERER', ''),
            'comment_type': 'comment',
            'comment_author': comment.user_name.encode('utf-8'),
        }

        if ak.comment_check(comment.comment.encode('utf-8'), data=data, build_data=True):
            comment.flags.create(
                user=comment.content_object.author,
                flag='spam'
            )
            comment.is_public = False
            comment.save()

comment_was_posted.connect(on_comment_was_posted)

