from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from knesset.mks.urls import mksurlpatterns
from knesset.laws.urls import lawsurlpatterns
from knesset.hashnav.views import SimpleView
admin.autodiscover()

js_info_dict = {
    'packages': ('knesset',),
    }

about_view = SimpleView(template='about.html')
main_view = SimpleView(template='main.html')

urlpatterns = patterns('',
    #url(r'^$', redirect_to, {'url' : 'main/'} ),
    url(r'^$', main_view, name='main'),
    #url(r'^main/$', main_view, name='main'),
    url(r'^about/$', about_view, name='about'),
    (r'^api/', include('knesset.api.urls')),
    (r'^profiles/', include('knesset.accounts.urls')),
    (r'^accounts/', include('socialauth.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^comments/', include('django.contrib.comments.urls')),
     (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

)
urlpatterns += mksurlpatterns + lawsurlpatterns
if settings.LOCAL_DEV:
    urlpatterns += patterns('django.views.static',
        (r'^%s(?P<path>.*)' % settings.MEDIA_URL[1:], 'serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
