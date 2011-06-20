from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

from planet import views as planet_views
from hitcount.views import update_hit_count_ajax
from backlinks.trackback.server import TrackBackServer
from backlinks.pingback.server import default_server

from knesset import feeds
from knesset.sitemap import sitemaps
from knesset.mks.urls import mksurlpatterns
from knesset.laws.urls import lawsurlpatterns
from knesset.committees.urls import committeesurlpatterns
from knesset.mks.views import get_mk_entry, mk_is_backlinkable

from knesset.auxiliary.views import main, post_annotation, post_details, \
    RobotsView, AboutView, CommentsView

admin.autodiscover()

js_info_dict = {
    'packages': ('knesset',),
}

# monkey patching the planet app
planet_views.post_detail = post_details

urlpatterns = patterns('',
    
    url(r'^$', main, name='main'),
    url(r'^about/$', AboutView.as_view(), name='about'),
    (r'^robots\.txt$', RobotsView.as_view()),
    (r'^api/', include('knesset.api.urls')),
    (r'^agenda/', include('knesset.agendas.urls')),
    (r'^users/', include('knesset.user.urls')),    
    (r'^badges/', include('knesset.badges.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^comments/$', CommentsView.as_view()), 
     url(r'^comments/delete/(?P<comment_id>\d+)/$', 'knesset.utils.delete', name='comments-delete-comment'),
     url(r'^comments/post/','knesset.utils.comment_post_wrapper',name='comments-post-comment'),
     (r'^comments/', include('django.contrib.comments.urls')),
     (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
     #(r'^search/', include('haystack.urls')),
     url(r'^search/', 'knesset.auxiliary.views.search', name='site-search'),
     (r'^feeds/comments/$', feeds.Comments()),
     (r'^feeds/votes/$', feeds.Votes()),
     (r'^feeds/bills/$', feeds.Bills()),
     (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}), 
     (r'^planet/', include('planet.urls')),
     url(r'^ajax/hit/$', update_hit_count_ajax, name='hitcount_update_ajax'),
     (r'^annotate/write/$', post_annotation, {}, 'annotatetext-post_annotation'),
     (r'^annotate/', include('annotatetext.urls')),
     (r'^avatar/', include('avatar.urls')),
     url(r'^pingback/', default_server, name='pingback-server'),
     url(r'^trackback/member/(?P<object_id>\d+)/$', TrackBackServer(get_mk_entry, mk_is_backlinkable),name='member-trackback'),
)
urlpatterns += mksurlpatterns + lawsurlpatterns + committeesurlpatterns
if settings.LOCAL_DEV:
    urlpatterns += patterns('django.views',
        (r'^static/(?P<path>.*)' , 'static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
