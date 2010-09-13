from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, \
                        HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotAllowed
from django.contrib.auth import login, authenticate
from forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User

from datetime import datetime, timedelta

from annotatetext.models import Annotation
from actstream import unfollow, follow
from actstream.models import Action
from forms import EditProfileForm

from knesset.accounts.models import EmailValidation
from knesset.mks.models import Member
from knesset.agendas.models import Agenda
from knesset.hashnav import DetailView, ListView
from knesset.tagvotes.models import TagVote

class PublicUserProfile(DetailView):

    queryset = User.objects.all()
    template_resource_name = 'viewed_user' # can't be 'user' because that name is 
                                           # overriden by request context processor!
    slug_field='username'

    def get_context(self):
        context = super(PublicUserProfile, self).get_context()
        context['annotations'] = Annotation.objects.filter(user = context['viewed_user'])
        context['tagged_items'] = TagVote.objects.filter(user = context['viewed_user'])
        return context


class ProfileListView(ListView):

    queryset = User.objects.order_by('username')
    template_name = 'user/profile_list.html'

class AggregatedAction:
    def __init__(self, actor, verb):
        self.actor = actor
        self.verb = verb
        self.targets = {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        return self.actor.__str__()+" "+self.verb.__str__()+" "+self.targets.__str__()

AGGREGATION_BREAK_PERIOD = timedelta(0, 15*60) #15 minutes

def aggregate_stream(actions):
    aggr_stream = []
    
    aggr_action = None
    for action in actions:
        if aggr_action is None: # first item in the action list
            pass
        elif aggr_action.verb != action.verb or aggr_action.actor != action.actor or (aggr_action.timestamp-action.timestamp)>AGGREGATION_BREAK_PERIOD:
            # break aggregation
            aggr_stream.append(aggr_action)
        elif aggr_action.targets.has_key(action.target):
            aggr_action.targets[action.target] += 1
            continue
        else:
            aggr_action.targets[action.target] = 1;
            continue
        
        # create a new aggregated action based on the current action
        aggr_action = AggregatedAction(action.actor, action.verb)
        aggr_action.targets[action.target] = 1
        aggr_action.timestamp = action.timestamp
  
    # add the last aggregated action to the stream
    if aggr_action is not None:
        aggr_stream.append(aggr_action)
            
    return aggr_stream

def create_user(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password1'])
            login(request, user)
            EmailValidation.objects.send(user=user)
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
            edit_form.save()
            m = request.user.message_set.create()
            m.message = 'Your profile has been updated.'
            m.save()
            return HttpResponseRedirect('.')

    if request.method == 'GET':
        edit_form = EditProfileForm(user = request.user)    
    return render_to_response('user/editprofile.html',
        context_instance=RequestContext(request,
            {'edit_form': edit_form,
            }))

def follow_members(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(reverse('login'))
    if request.method == 'POST':
        unwatch_id = request.POST.get('unwatch', None)
        if unwatch_id:
            member = get_object_or_404(Member, pk=unwatch_id)
            unfollow(request.user, member, send_action=True)
        else:
            watch_id = request.POST.get('watch', None)
            if not watch_id:
                return HttpResponseServerError('neither "watch" nor "unwatch" arguments specified')
            try:
                member = get_object_or_404(Member, pk=watch_id)
                follow(request.user, member)
            except Member.DoesNotExist:
                return HttpResponseBadRequest('bad member id')
        return HttpResponse('OK')
    else:
        return HttpResponseNotAllowed(['POST'])

def follow_agendas(request):
    if not request.user.is_authenticated():
        return HttpResponseForbidden(reverse('login'))
    if request.method == 'POST':
        unwatch_id = request.POST.get('unwatch', None)
        if unwatch_id:
            agenda = get_object_or_404(Agenda, pk=unwatch_id)
            unfollow(request.user, agenda, send_action=True)
        else:
            watch_id = request.POST.get('watch', None)
            if not watch_id:
                return HttpResponseServerError('neither "watch" nor "unwatch" arguments specified')
            try:
                agenda = get_object_or_404(Agenda, pk=watch_id)
                follow(request.user, agenda)
            except Agenda.DoesNotExist:
                return HttpResponseBadRequest('bad agenda id')
        return HttpResponse('OK')
    else:
        return HttpResponseNotAllowed(['POST'])
