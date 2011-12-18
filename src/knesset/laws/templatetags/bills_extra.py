#encoding: utf-8
import json

from django import template
from django.conf import settings


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

def split_member_vote_list_by_party(member_vote_list):
    ''' create a party patrtitioned list of "for" voters and "against" voters '''

    list_by_party = []
    if member_vote_list.count() > 0:
        ''' first party, first member '''
        curr_party = { 'party' : member_vote_list[0].member.current_party.name,
                      'members' : []}
        for vote in member_vote_list:
            member = {'name' : vote.member.name}
            if vote.member.current_party.name == curr_party['party']:
                curr_party['members'].append(member)
            else:
                list_by_party.append(curr_party)
                curr_party = { 'party' : vote.member.current_party.name,
                      'members' : [member]}
        ''' last party '''
        list_by_party.append(curr_party)
    return list_by_party

@register.inclusion_tag('laws/bill_inabox.html')
def bill_inabox(bill):
    """ TODO: firstX and not first3"""

    bill_inabox_dict = dict({ 'MEDIA_URL' : settings.MEDIA_URL,
                 'bill': bill,
            'proposers_first3' : bill.proposers.all()[:3],
            'proposers_count_minus3' : bill.proposers.count() - 3})

    if bill.pre_votes.count() > 0:
        pre_vote = bill.pre_votes.all()[bill.pre_votes.count() - 1]
        for_vote_sorted = pre_vote.for_votes().order_by('member__current_party')
        pre_vote_for_votes = split_member_vote_list_by_party(for_vote_sorted)
        against_vote_sorted = bill.pre_votes.all()[bill.pre_votes.count() - 1].against_votes().order_by('member__current_party')
        pre_vote_against_votes = split_member_vote_list_by_party(against_vote_sorted)

        pre_vote_drill_data = dict({ 'against' : dict({ 'count' : against_vote_sorted.count(),
                                              'votes' : pre_vote_against_votes}),
                                    'for' : dict({ 'count' : for_vote_sorted.count(),
                                              'votes' : pre_vote_for_votes})})

        pre_vote_dict = dict({'pre_vote' : pre_vote,
                              'pre_vote_drill_data' : json.dumps(pre_vote_drill_data),
                              'pre_vote_passed' : pre_vote.against_votes_count < pre_vote.for_votes_count,
#                              'pre_vote_for_votes_grouped_by_parties' : pre_vote_for_votes_grouped_by_parties,
                              'pre_vote_time' : {'day' : pre_vote.time.day,
                               'month' : pre_vote.time.month,
                               'year' : pre_vote.time.year}})
        bill_inabox_dict = dict(bill_inabox_dict.items() + pre_vote_dict.items())

    # what is the real index? 0 is not the correct one
    return bill_inabox_dict