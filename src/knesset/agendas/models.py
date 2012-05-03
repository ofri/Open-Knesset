from operator import itemgetter, attrgetter

from django.db import models
from django.db.models import Sum, Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.conf import settings

from django.contrib.auth.models import User
from actstream.models import Follow
from knesset.laws.models import VoteAction
from knesset.mks.models import Party, Member
import queries

AGENDAVOTE_SCORE_CHOICES = (
    ('',_("Not selected")),
    (-1.0, _("Opposes fully")),
    (-0.5, _("Opposes partially")),
    (0.0, _("Agnostic")),
    (0.5, _("Complies partially")),
    (1.0, _("Complies fully")),
)
IMPORTANCE_CHOICES = (
    ('',_("Not selected")),
    (0.0, _("Marginal Importance")),
    (0.3, _("Medium Importance")),
    (0.6, _("High Importance")),
    (1.0, _("Very High Importance")),
)

class UserSuggestedVote(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='user_suggested_votes')
    vote = models.ForeignKey('laws.Vote', related_name='user_suggested_agendas')
    reasoning = models.TextField(blank=True, default='')
    user = models.ForeignKey(User, related_name='suggested_agenda_votes')
    sent_to_editor = models.BooleanField(default=False)

    class Meta:
        unique_together = ('agenda','vote','user')



class AgendaVote(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='agendavotes')
    vote = models.ForeignKey('laws.Vote', related_name='agendavotes')
    score = models.FloatField(default=0.0, choices=AGENDAVOTE_SCORE_CHOICES)
    importance = models.FloatField(default=1.0, choices=IMPORTANCE_CHOICES)
    reasoning = models.TextField(null=True,blank=True)

    def get_score_header(self):
        return _('Position')

    class Meta:
        unique_together= ('agenda', 'vote')

class AgendaMeeting(models.Model):
    agenda = models.ForeignKey('Agenda', related_name='agendameetings')
    meeting = models.ForeignKey('committees.CommitteeMeeting',
                                related_name='agendacommitteemeetings')
    score = models.FloatField(default=0.0, choices=IMPORTANCE_CHOICES)
    reasoning = models.TextField(null=True)

    def get_score_header(self):
        return _('Importance')

    class Meta:
        unique_together = ('agenda', 'meeting')

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
    _mks_grade = None

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

    def get_relevant_for_mk(self, mk, agendaId):
        agendas = AgendaVote.objects.filter(agenda__id=agendaId,vote__votes__id=mk).distinct()
        return agendas

    def get_relevant_for_user(self, user):
        if user == None or not user.is_authenticated():
            agendas = Agenda.objects.filter(is_public=True)
        elif user.is_superuser:
            agendas = Agenda.objects.all()
        else:
            agendas = Agenda.objects.filter(Q(is_public=True) | Q(editors=user)).distinct()
        return agendas

    def get_possible_to_suggest(self, user, vote):
        if user == None or not user.is_authenticated():
            agendas = Agenda.objects.none()
        else:
            agendas = Agenda.objects.filter(is_public=True)\
                            .exclude(editors=user)\
                            .exclude(agendavotes__vote=vote)\
                            .distinct()
        return agendas

    def get_mks_grade(self):
        if not self._mks_grade:
            self._mks_grade = cache.get('agendas_mks_grade')
            if not self._mks_grade:
                self._mks_grade = queries.agendas_mks_grade()
                cache.set('agendas_mks_grade', self._mks_grade, 1800)
        return self._mks_grade

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
        return "%s %s %s" % (self.name,_('edited by'),self.public_owner_name)

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
        for_score = sum(
                AgendaVote.objects.filter(
                    agenda=self,
                    vote__voteaction__member=member,
                    vote__voteaction__type="for").extra(
                select={'weighted_score':'agendas_agendavote.score*agendas_agendavote.importance'}).values_list('weighted_score',flat=True))
        against_score = sum(
                AgendaVote.objects.filter(
                    agenda=self,
                    vote__voteaction__member=member,
                    vote__voteaction__type="against").extra(
                select={'weighted_score':'agendas_agendavote.score*agendas_agendavote.importance'}).values_list('weighted_score',flat=True))

        max_score = sum([abs(x['score']*x['importance']) for x in
                         self.agendavotes.values('score','importance')])
        if max_score > 0:
            return (for_score - against_score) / max_score * 100
        else:
            return 0.0

    def party_score(self, party):
        # party_members_ids = party.members.all().values_list('id',flat=True)
        for_score = sum(map(itemgetter('weighted_score'),
                            AgendaVote.objects.filter(
                                agenda=self,
                                vote__voteaction__member__in=party.members.all(),
                                vote__voteaction__type="for").extra(
                            select={'weighted_score':'agendas_agendavote.score*agendas_agendavote.importance'}).values('weighted_score')))
        against_score = sum(map(itemgetter('weighted_score'),
                            AgendaVote.objects.filter(
                                agenda=self,
                                vote__voteaction__member__in=party.members.all(),
                                vote__voteaction__type="against").extra(
                            select={'weighted_score':'agendas_agendavote.score*agendas_agendavote.importance'}).values('weighted_score')))

        #max_score = sum([abs(x) for x in self.agendavotes.values_list('score', flat=True)]) * party.members.count()
        max_score = sum([abs(x['score']*x['importance']) for x in
                         self.agendavotes.values('score','importance')]) * party.number_of_seats
        if max_score > 0:
            return (for_score - against_score) / max_score * 100
        else:
            return 0.0

    def number_of_followers(self):
        n = cache.get('agenda_%d_num_followers' % self.id, None)
        if n is None:
            n = Follow.objects.filter(content_type=ContentType.objects.get(app_label="agendas", model="agenda").id,object_id=self.id).count()
            cache.set('agenda_%d_num_followers' % self.id, n,
                      settings.LONG_CACHE_TIME)
        return n

    def related_mk_votes(self,member):
        # Find all votes that
        #   1) This agenda is ascribed to
        #   2) the member participated in and either voted for or against
        # for_votes      = AgendaVote.objects.filter(agenda=self,vote__voteaction__member=member,vote__voteaction__type="for").distinct()
        #against_votes   = AgendaVote.objects.filter(agenda=self,vote__voteaction__member=member,vote__voteaction__type="against").distinct()
        vote_actions = VoteAction.objects.filter(member=member,vote__agendavotes__agenda=self)
        all_votes = AgendaVote.objects.filter(agenda=self,vote__voteaction__member=member).distinct()
        # TODO: improve ugly code below
        member_votes = list()
        for member_vote in all_votes:
            for vote_action in vote_actions:
                if (vote_action.vote == member_vote.vote):
                    member_votes.insert(0,member_vote)
                    member_votes[0].voteaction = vote_action

        return member_votes
        #return AgendaVote.objects.filter(agenda=self,vote__voteaction__member=mk).distinct()

    def selected_instances(self, cls, top=3, bottom=3):
        instances = list(cls.objects.all())
        for instance in instances:
            instance.score = self.__getattribute__('%s_score' % instance.__class__.__name__.lower())(instance)
        instances.sort(key=attrgetter('score'))
        instances = get_top_bottom(instances, top, bottom)
        instances['top'].sort(key=attrgetter('score'), reverse=True)
        instances['bottom'].sort(key=attrgetter('score'), reverse=True)
        return instances

    def get_mks_grade(self):
        mks_grade = Agenda.objects.get_mks_grade()
        return mks_grade.get(self.id,[])

from listeners import *
