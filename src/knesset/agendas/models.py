from operator import itemgetter, attrgetter

from django.db import models
from django.db.models import Sum, Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from actstream.models import Follow 

from knesset.mks.models import Party, Member

score_text_to_score = {'complies-fully':         1.0,
                       'complies-partially':     0.5,
                       'agnostic':               0.0,
                       'opposes-partially':     -0.5,
                       'opposes-fully':         -1.0,
                       }

score_to_score_text = dict(zip(score_text_to_score.values(), score_text_to_score.keys()))

class AgendaVote(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='related_votes')
    vote = models.ForeignKey('laws.Vote')
    score = models.FloatField(default=0.0)
    reasoning = models.TextField(null=True,blank=True)

    class Meta:
        unique_together= ('agenda', 'vote')
    
    def set_score_by_text(self,score_text):
        self.score = score_text_to_score[score_text]
    def get_text_score(self):
        try:
            return score_to_score_text[self.score]
        except KeyError:
            return None
    
def get_top_bottom(lst, top, bottom):
    """
    Returns a cropped list, keeping some of the list's top and bottom.
    Edge conditions are handled gracefuly.
    Input list should be ascending so that top is at the end. 
    """
    if len(lst) < top+bottom:
        delta = top+bottom - len(lst)
        bottom = bottom - delta/2
        if delta%2:
            top = top - delta/2 -1
        else:
            top = top - delta/2
    if top and bottom:
        top_lst = lst[-top:]
        bottom_lst = lst[:bottom]
    elif top:
        top_lst = lst[-top:]
        bottom_lst = []
    elif bottom:
        top_lst = []
        bottom_lst = lst[:bottom]
    else:
        top_lst = []
        bottom_lst = []
        
    return {'top':top_lst,
            'bottom':bottom_lst}
    

class AgendaManager(models.Manager):
    def get_selected_for_instance(self, instance, user=None, top=3, bottom=3):
        # Returns interesting agendas for model instances such as: member, party
        agendas = list(self.get_relevant_for_user(user))
        for agenda in agendas:
            agenda.score = agenda.__getattribute__('%s_score' % instance.__class__.__name__.lower())(instance)
            agenda.significance = agenda.score * agenda.number_of_followers()
        agendas.sort(key=attrgetter('significance'))
        agendas = get_top_bottom(agendas, top, bottom)
        agendas['top'].sort(key=attrgetter('score'), reverse=True)
        agendas['bottom'].sort(key=attrgetter('score'), reverse=True)
        return agendas
    
    def get_relevant_for_user(self, user):
        if user == None:
            agendas = self.filter(is_public=True)
        elif user.is_superuser:
            agendas = self.all()
        else:
            agendas = self.filter(Q(is_public=True) | Q(editors=user)).distinct()
        return agendas

           
class Agenda(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True,blank=True)
    editors = models.ManyToManyField('auth.User', related_name='agendas')
    votes = models.ManyToManyField('laws.Vote',through=AgendaVote)
    public_owner_name = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)
    
    objects = AgendaManager()
    
    class Meta:
        verbose_name = _('Agenda')
        verbose_name_plural = _('Agendas')
        unique_together = (("name", "public_owner_name"),)

    def __unicode__(self):
        return "%s %s %s" % (self.name,_('by'),self.public_owner_name)
    
    @models.permalink
    def get_absolute_url(self):
        return ('agenda-detail', [str(self.id)])

    @models.permalink
    def get_edit_absolute_url(self):
        return ('agenda-detail-edit', [str(self.id)])
    
    def member_score(self, member):
        # Find all votes that
        #   1) This agenda is ascribed to
        #   2) the member participated in and either voted for or against
        for_score       = AgendaVote.objects.filter(agenda=self,vote__voteaction__member=member,vote__voteaction__type="for").distinct().aggregate(Sum('score'))['score__sum'] or 0
        against_score   = AgendaVote.objects.filter(agenda=self,vote__voteaction__member=member,vote__voteaction__type="against").distinct().aggregate(Sum('score'))['score__sum'] or 0
        max_score = sum([abs(x) for x in self.agendavote_set.values_list('score', flat=True)])
        if max_score > 0:
            return (for_score - against_score) / max_score * 100
        else:
            return 0.0
    
    def party_score(self, party):
        # party_members_ids = party.members.all().values_list('id',flat=True)
        for_score       = AgendaVote.objects.filter(agenda=self,vote__voteaction__member__in=party.members.all(),vote__voteaction__type="for").aggregate(Sum('score'))['score__sum'] or 0
        against_score   = AgendaVote.objects.filter(agenda=self,vote__voteaction__member__in=party.members.all(),vote__voteaction__type="against").aggregate(Sum('score'))['score__sum'] or 0
        max_score = sum([abs(x) for x in self.agendavote_set.values_list('score', flat=True)]) * party.members.count()
        if max_score > 0:
            return (for_score - against_score) / max_score * 100
        else:
            return 0.0

    def number_of_followers(self):
        return Follow.objects.filter(content_type=ContentType.objects.get(app_label="agendas", model="agenda").id,object_id=self.id).count()
    
    def selected_instances(self, cls, top=3, bottom=3):
        instances = list(cls.objects.all())
        for instance in instances:
            instance.score = self.__getattribute__('%s_score' % instance.__class__.__name__.lower())(instance)
        instances.sort(key=attrgetter('score'))
        instances = get_top_bottom(instances, top, bottom)
        instances['top'].sort(key=attrgetter('score'), reverse=True)
        instances['bottom'].sort(key=attrgetter('score'), reverse=True)
        return instances
        
from listeners import *
