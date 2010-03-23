from django.conf.urls.defaults import *

# views coded inthis app
urlpatterns = patterns('knesset.user.views',
    url(r'^create/$', 'create_user', name ='create_user'),
    )

# views coded elsewhere
urlpatterns += patterns('',
    (r'^soc/', include('socialauth.urls')),
    (r'^registration/', include('knesset.accounts.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', 
        {'template_name': 'user/login.html'}, name='login')
    )

