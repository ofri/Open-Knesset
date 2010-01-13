#encoding: UTF-8
from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns ('',
    url(r'^edit-profile/$', edit_profile, name='edit-profile'),
    url(r'^send-validation-email/$', send_validation_email, name='send-validation-email'),
    url(r'^validate-email/(?P<key>.*)/$', validate_email, name='validate-email'),
)
