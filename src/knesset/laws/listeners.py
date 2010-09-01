#encoding: utf-8
from django.db.models.signals import m2m_changed
from django.contrib.contenttypes.models import ContentType
from actstream import action
from actstream.models import Action
from knesset.utils import cannonize, disable_for_loaddata
from knesset.laws.models import PrivateProposal
from knesset.mks.models import Member

def record_bill_proposal(**kwargs):
    if kwargs['action'] != "post_add":
        return
    private_proposal_ct = ContentType.objects.get(app_label="laws", model="privateproposal")
    member_ct = ContentType.objects.get(app_label="mks", model="member")
    proposal = kwargs['instance']
    if str(kwargs['sender']).find('proposers')>=0:
        verb = 'proposed'
    else:
        verb = 'joined'
    for mk_id in kwargs['pk_set']:
        if Action.objects.filter(actor_object_id=mk_id, actor_content_type=member_ct, verb=verb, target_object_id=proposal.id, 
                target_content_type=private_proposal_ct).count()==0:
            mk = Member.objects.get(pk=mk_id)
            action.send(mk, verb=verb, target=proposal, timestamp=proposal.date)

m2m_changed.connect(record_bill_proposal, sender=PrivateProposal.proposers.through)
m2m_changed.connect(record_bill_proposal, sender=PrivateProposal.joiners.through) # same code handles both events
