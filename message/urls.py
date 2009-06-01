from django.conf.urls.defaults import *

from fivesongs.message import views

urlpatterns = patterns('',
    url(r'^$',                      views.show_all,        name='messages_all'),
)

