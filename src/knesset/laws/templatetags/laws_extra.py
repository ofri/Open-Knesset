from django import template
from tagging.models import Tag, TaggedItem
from knesset.tagvotes.models import TagVote
from knesset.laws.models import VoteAction, VOTE_ACTION_TYPE_CHOICES, MemberVotingStatistics
from knesset.mks.models import Member
from datetime import date, timedelta
from django.utils.translation import ugettext_lazy as _
import logging
logger = logging.getLogger("open-knesset.laws.templatetags")


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
    width = round((number-baseline)/norm_factor,1)
    return {'width': width, 'is_for':is_for}

@register.filter
def recent_discipline(m):
    d = date.today() - timedelta(30)
    try:
        return m.voting_statistics.discipline(d) or _('Not enough data')
    except MemberVotingStatistics.DoesNotExist:
        logger.error('%d is missing voting statistics' % m.id)
        return _('Not enough data')

@register.filter
def recent_coalition_discipline(m):
    d = date.today() - timedelta(30)
    try:
        return m.voting_statistics.coalition_discipline(d) or _('Not enough data')
    except MemberVotingStatistics.DoesNotExist:
        logger.error('%d is missing voting statistics' % m.id)
        return _('Not enough data')

@register.filter
def recent_votes_count(m):
    d = date.today() - timedelta(30)
    try:
        return m.voting_statistics.votes_count(d)
    except MemberVotingStatistics.DoesNotExist:
        logger.error('%d is missing voting statistics' % m.id)
        return _('Not enough data')


@register.inclusion_tag('laws/_member_stand.html')
def member_stand(v, m):
    """ returns member m stand on vote v """
    va = VoteAction.objects.filter(member = m, vote = v)
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
            return {'stand':stand, 'class':cls, 'name':m.name}
        except Exception, e:
            print e
            return 

@register.inclusion_tag('laws/_paginator.html')
def pagination(page_obj, paginator, request):
    """ includes links to previous/next page, and other pages if needed """
    base_link = '&'.join(["%s=%s" % (k,v) for (k,v) in request.GET.items() if k!='page'])
    if paginator.num_pages <= 10:
        show_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(1, paginator.num_pages+1)]
        show_pages[page_obj.number-1][2] = True
    else:
        if page_obj.number <= 5:
            show_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(1, page_obj.number+3)]
            last_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(paginator.num_pages-1, paginator.num_pages+1)]
        elif page_obj.number >= paginator.num_pages-5:
            show_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(page_obj.number-2, paginator.num_pages+1)]
            first_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(1, 3)]
        else:
            first_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(1, 3)]
            last_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(paginator.num_pages-1, paginator.num_pages+1)]
            show_pages = [[x,"?%s&page=%d"%(base_link,x),False] for x in range(page_obj.number-2, page_obj.number+3)]
            
        for i in show_pages:
            if i[0]==page_obj.number:
                i[2] = True

    return locals()
  
