from django import template
from tagging.models import Tag, TaggedItem
from knesset.tagvotes.models import TagVote
from knesset.laws.models import VoteAction, VOTE_ACTION_TYPE_CHOICES
from knesset.mks.models import Member
from datetime import date, timedelta
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('laws/_tag_vote.html')
def user_votes(user, vote, tag):
    ti = TaggedItem.objects.filter(tag=tag).filter(object_id=vote.id)[0]
    try:
        tv = TagVote.objects.filter(tagged_item=ti, user=user)[0]
        cv = tv.vote
    except Exception:
        cv = 0
    return {'user': user, 'vote':vote, 'tag':tag, 'current_vote_up':cv==1, 'current_vote_down':cv==-1}

@register.inclusion_tag('laws/_bar.html')
def bar(number, is_for, norm_factor=1.2, baseline=0):
    """ draws a bar to represent number of voters.
        number - number of people voted this way.
        is_for - is this a "for" bar. false means "against" bar.
    """
    width = round((number-baseline)/norm_factor)
    return {'width': width, 'is_for':is_for}

@register.filter
def recent_discipline(m):
    d = date.today() - timedelta(30)
    return m.voting_statistics.discipline(d) or _('Not enough data')

@register.filter
def recent_coalition_discipline(m):
    d = date.today() - timedelta(30)
    return m.voting_statistics.coalition_discipline(d) or _('Not enough data')

@register.filter
def recent_votes_count(m):
    d = date.today() - timedelta(30)
    return m.voting_statistics.votes_count(d)

@register.inclusion_tag('laws/_member_stand.html')
def member_stand(v, m):
    """ returns member m stand on vote v """
    va = VoteAction.objects.filter(member__id = m, vote__id = v)
    if va:
        for (name,string) in VOTE_ACTION_TYPE_CHOICES:
            if va[0].type==name:
                stand = _(string)
                cls = name
        return {'stand':stand, 'class':cls, 'name':va[0].member.name}
    else:
        stand=_('Absent')
        cls = 'absent'
        try:
            m = Member.objects.get(pk=m)
            return {'stand':stand, 'class':cls, 'name':m.name}
        except Exception, e:
            print e
            return 

