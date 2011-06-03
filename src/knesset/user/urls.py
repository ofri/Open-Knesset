from django.conf.urls.defaults import *
from views import PublicUserProfile, ProfileListView

profile_list = ProfileListView()
user_public_profile = PublicUserProfile.as_view(template_name='user/public_profile.html')
user_tagged_items = PublicUserProfile.as_view(template_name='user/tagged_items.html')
user_annotated_items = PublicUserProfile.as_view(template_name='user/annotated_items.html')

# views coded in this app
urlpatterns = patterns('knesset.user.views',
    url(r'^create/$', 'create_user', name ='register'),
    url(r'^members/$', 'follow_members', name ='follow-members'),
    url(r'^bills/$', 'follow_bills', name='follow-bills'),
    url(r'^agendas/$', 'follow_agendas', name ='follow-agendas'),
    url(r'^edit-profile/$', 'edit_profile', name='edit-profile'),
    url(r'^unfollow/$', 'user_unfollows', name='user-unfollows'),
    )

# auth views
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'user/login.html'}, name='login'),
    url(r'^logout/$', 'logout_then_login', name='logout'),
    url(r'^password_reset/$', 'password_reset', {'template_name': 'user/password_reset_form.html'}, name='password_reset'),
    url(r'^password_reset/done/$', 'password_reset_done', {'template_name': 'user/password_reset_done.html'}),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {'template_name': 'user/password_reset_confirm.html'}),
    url(r'^reset/done/$', 'password_reset_complete', {'template_name': 'user/password_reset_complete.html'}),
    )

urlpatterns += patterns('',
    (r'^registration/', include('knesset.accounts.urls')),
    url(r'^(?P<pk>\d+)/$', user_public_profile, name='public-profile'),
    url(r'^(?P<slug>.+)/tagged/$', user_tagged_items, name='user-tagged-items'),
    url(r'^(?P<slug>.+)/annotated/$', user_annotated_items, name='user-annotated-items'),
    url(r'^(?P<slug>.+)/$', user_public_profile, name='public-profile'),
    url(r'^$', profile_list, name='profile-list'),
    )
