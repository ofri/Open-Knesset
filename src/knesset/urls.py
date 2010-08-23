from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.decorators.cache import cache_page

from django.contrib.comments.models import Comment
from django.contrib import admin

from knesset.mks.urls import mksurlpatterns
from knesset.laws.urls import lawsurlpatterns
from knesset.committees.urls import committeesurlpatterns
from knesset.hashnav.views import SimpleView
from search_sites import SearchFormWithSpellSuggest
from haystack.views import SearchView
from haystack.forms import SearchForm

admin.autodiscover()

from knesset.feeds import *
from knesset.sitemap import sitemaps

feeds = {
    'comments': Comments,
    'votes': Votes
}


js_info_dict = {
    'packages': ('knesset',),
    }

about_view = SimpleView(template='about.html')
#comment_view = object_list(Comment.objects.all(), template_name='comments/comments.html')

#main_view = SimpleView(template='main.html')
from knesset.auxiliary.views import main

urlpatterns = patterns('',
    url(r'^$', cache_page(main, 60*10), name='main'),
    url(r'^about/$', about_view, name='about'),
    (r'^api/', include('knesset.api.urls')),
    (r'^user/', include('knesset.user.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^comments/$', 'django.views.generic.list_detail.object_list', {'queryset': Comment.objects.all(),'paginate_by':20}), 
     url(r'^comments/post/','knesset.utils.comment_post_wrapper',name='comments-post-comment'),
     (r'^comments/', include('django.contrib.comments.urls')),
     (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
     #(r'^search/', include('haystack.urls')),
     url(r'^search/', SearchView(form_class=SearchFormWithSpellSuggest), name='haystack_search'),
     (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',{'feed_dict': feeds}),
     (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}), 
     (r'^planet/', include('planet.urls')),
     (r'^annotate/', include('annotatetext.urls')),

)
urlpatterns += mksurlpatterns + lawsurlpatterns + committeesurlpatterns
if settings.LOCAL_DEV:
    urlpatterns += patterns('django.views',
        (r'^static/(?P<path>.*)' , 'static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
