from django.http import HttpResponse, HttpResponseRedirect,HttpResponseForbidden
from django.contrib.auth import login, authenticate
from forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from forms import EditProfileForm

from knesset.accounts.models import EmailValidation
from knesset.mks.models import Member

def create_user(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password1'])
            login(request, user)
            ev = EmailValidation.objects.send(user=user)
            next = request.POST.get('next', None)
            return HttpResponseRedirect(next if next else reverse('edit-profile'))
        else:
            return render_to_response('user/create_user.html',
                        context_instance=RequestContext(request, {'form': form}))
    form = RegistrationForm()
    return render_to_response('user/create_user.html',
                context_instance=RequestContext(request, {'form': form,
                    'next': request.GET.get('next','')}))

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
    return render_to_response('user/editprofile.html',
        context_instance=RequestContext(request,
            {'edit_form': edit_form,
            }))

def follow_members(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(reverse('login'))
    p = request.user.get_profile()
    if request.method == 'POST':
        unwatch_id = request.POST.get('unwatch', None)
        if unwatch_id:
            p.followed_members.remove(int(unwatch_id))
        else:
            watch_id = request.POST.get('watch', None)
            if not watch_id:
                return HttpResponseServerError('neither "watch" nor "unwatch" arguments specified')
            try:
                member = Member.objects.get(pk=watch_id)
                p.followed_members.add(member)
            except Member.DoesNotExist:
                return HttpResponseBadRequest('bad member id')
        return HttpResponse('OK')
    else:
        return HttpResponseNotAllowed(['POST'])
