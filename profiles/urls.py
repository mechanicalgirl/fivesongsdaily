from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views

from fivesongs.profiles import views

urlpatterns = patterns('',
    url(r'^(?P<username>\w+)/$',        views.view,             name='profiles_view'),
    url(r'^(?P<username>\w+)$',		views.view,		name='profiles_view'),

    url(r'^edit/(?P<username>\w+)/$',   views.edit,             name='profiles_edit'),
    url(r'^edit/(?P<username>\w+)$',	views.edit,		name='profiles_edit'),

    url(r'^band/(?P<bandname>.*?)/$',   views.searchband,	name='profiles_searchband'),
    url(r'^band/(?P<bandname>.*?)$',    views.searchband,       name='profiles_searchband'),
)
