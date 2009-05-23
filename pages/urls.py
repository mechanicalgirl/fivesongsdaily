from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('django.views.generic.simple',
    (r'^about/$',	'direct_to_template', {'template': 'about.html'}),
    (r'^$',		'direct_to_template', {'template': 'about.html'}),
)

