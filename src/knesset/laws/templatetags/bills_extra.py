#encoding: utf-8
from django import template

register = template.Library()

@register.inclusion_tag('laws/bill_full_name.html')
def bill_full_name(bill):
    return { 'bill': bill }

@register.inclusion_tag('laws/bill_list_item.html')
def bill_list_item(bill):
    return { 'bill': bill }

@register.inclusion_tag('laws/item_tags.html')
def item_tags(tags):
    return { 'tags': tags }

@register.inclusion_tag('laws/bill_inabox.html')
def bill_inabox(bill):
    """ TODO: firstX and not first3"""

#    CONVERT_TO_DISCUSSION_HEADERS = ('להעביר את הנושא'.decode('utf8'), 'העברת הנושא'.decode('utf8'))

#    discussion = False
#    for v in bill.pre_votes.all():
#        for h in CONVERT_TO_DISCUSSION_HEADERS:
#            if v.title.find(h)>=0: # converted to discussion
#                discussion = True
    pre_vote_count = bill.pre_votes.count()
    pre_vote_against_width = 0
    pre_vote_fields = {}
    if pre_vote_count > 0:
        pre_vote_last = bill.pre_votes.all()[pre_vote_count - 1]
        pre_vote_against_width = (pre_vote_last.against_votes_count() * 120) / (pre_vote_last.for_votes_count() + pre_vote_last.against_votes_count())
        pre_vote_fields = { 'pre_vote_against_width' : pre_vote_against_width,
                       'pre_vote_backgroundPosition' : pre_vote_against_width - 120,
                        # what is the real index? 0 is not the correct one
                        'pre_vote_passed' : bill.pre_votes.all()[0].for_votes_count() > bill.pre_votes.all()[0].against_votes_count(),
                        'pre_vote_date' : "%s/%s<br>%s" % (bill.pre_votes.all()[0].time.day, bill.pre_votes.all()[0].time.month, bill.pre_votes.all()[0].time.year)}

    return dict({ 'bill': bill,
            'proposers_first3' : bill.proposers.all()[:3],
            'proposers_count_minus3' : bill.proposers.count() - 3,
#            'was_converted_to_discussion' : discussion,
            'was_pre_voted' : pre_vote_count > 0,
            'pre_vote_passed' : "",
            'pre_vote_date' : "?"}.items() + pre_vote_fields.items())
