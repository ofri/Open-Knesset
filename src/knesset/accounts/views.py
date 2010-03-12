from django.conf import settings
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission

from forms import EditProfileForm
from models import *

from django.core.mail import send_mail
import logging
import sys
logger = logging.getLogger("open-knesset.accounts")

@login_required
def edit_profile(request):
    if request.method == 'POST':
        edit_form = EditProfileForm(user=request.user, data=request.POST)
        if edit_form.is_valid():
            user = edit_form.save()
            m = request.user.message_set.create()
            m.message = 'Your profile has been updated.'
            m.save()
            
            return HttpResponseRedirect('.')
    if request.method == 'GET':
        edit_form = EditProfileForm(user = request.user)
    payload = {'edit_form':edit_form}
    return render_to_response('accounts/editprofile.html', payload, RequestContext(request))


@login_required
def send_validation_email(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('edit-profile'))
    ev = EmailValidation.objects.create(user=request.user)
    current_site = Site.objects.get_current()
    subject = render_to_string('accounts/email_validation_subject.txt',
                               { 'site': current_site })
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    
    message = render_to_string('accounts/email_validation.txt',
                               { 'activation_key': ev.activation_key,                                 
                                 'site': current_site })
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [ev.email])
    except Exception:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        logger.error("%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)))
    return render_to_response('accounts/email_validation_sent.html', {'email':ev.email}, RequestContext(request))

@login_required
def validate_email(request, key):
    (success, fail_reason) = EmailValidation.validate(request.user, key)
    if success:
        return render_to_response('accounts/email_validation_successful.html', {}, RequestContext(request))

    logger.info("email validation failed: %s", fail_reason)
    return render_to_response('accounts/email_validation_failed.html', {'reason':fail_reason}, RequestContext(request))

