from django import template
from tagging.models import Tag, TaggedItem
from knesset.tagvotes.models import TagVote

register = template.Library()

@register.inclusion_tag('laws/_tag_vote.html')
def user_votes(user, vote, tag):
    ti = TaggedItem.objects.filter(tag=tag).filter(object_id=vote.id)[0]
    try:
        tv = TagVote.objects.filter(tagged_item=ti, user=user)[0]
        cv = tv.vote
    except Exception:
        cv = 0
    print cv==1
    print cv==-1
    return {'user': user, 'vote':vote, 'tag':tag, 'current_vote_up':cv==1, 'current_vote_down':cv==-1}


