from django.conf.urls import url, patterns


urlpatterns = patterns('',
    #(r'^$', 'canvas'),
    url(r'^hello/$', 'knesset.simple.views.hello_world'),

    # Define other pages you want to create here
)
