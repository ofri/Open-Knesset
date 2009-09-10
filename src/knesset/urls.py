from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {'template': 'home.html'}, 'home'),
    (r'^member/$', include('knesset.mks.urls')),
    (r'^party/$', include('knesset.mks.urls')),
    (r'^vote/$', include('knesset.laws.urls')),
    (r'^api/', include('knesset.api.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^jsi18n/$', 'django.views.i18n.javascript_catalog'),

)
if settings.LOCAL_DEV:
    urlpatterns += patterns('django.views.static',
        (r'^%s(?P<path>.*)' % settings.MEDIA_URL[1:], 'serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
