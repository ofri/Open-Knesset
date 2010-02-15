from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
from django.views.generic.simple import redirect_to

from django.contrib.comments.models import Comment

from django.contrib import admin
from knesset.views import MainView
from knesset.mks.urls import mksurlpatterns
from knesset.laws.urls import lawsurlpatterns
from knesset.hashnav.views import SimpleView
admin.autodiscover()

from knesset.feeds import *

feeds = {
    'comments': Comments,
    'votes': Votes
}

js_info_dict = {
    'packages': ('knesset',),
    }

about_view = SimpleView(template='about.html')
#comment_view = object_list(Comment.objects.all(), template_name='comments/comments.html')

urlpatterns = patterns('',
    url(r'^$', MainView(), name='main'),
    url(r'^about/$', about_view, name='about'),
    (r'^api/', include('knesset.api.urls')),
    (r'^profiles/', include('knesset.accounts.urls')),
    (r'^accounts/', include('socialauth.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^comments/$', 'django.views.generic.list_detail.object_list', {'queryset': Comment.objects.all(),'paginate_by':20}), 
     (r'^comments/', include('django.contrib.comments.urls')),
     (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
     (r'^search/', include('haystack.urls')),
     (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',{'feed_dict': feeds}),
)
urlpatterns += mksurlpatterns + lawsurlpatterns
if settings.LOCAL_DEV:
    urlpatterns += patterns('django.views.static',
        (r'^%s(?P<path>.*)' % settings.MEDIA_URL[1:], 'serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
