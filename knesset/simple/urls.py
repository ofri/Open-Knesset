from django.conf.urls.defaults import *


urlpatterns = patterns('',
    #(r'^$', 'canvas'),
    (r'^hello/$', 'knesset.simple.views.hello_world'),

    # Define other pages you want to create here
)