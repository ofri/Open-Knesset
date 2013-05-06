from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

TYPE_CHOICES = (
    ('all', _('All votes')),
    ('law-approve', _('Law Approvals')),
    ('second-call', _('Second Call')),
    ('demurrer', _('Demurrer')),
    ('no-confidence', _('Motion of no confidence')),
    ('pass-to-committee', _('Pass to committee')),
    ('continuation', _('Continuation')),
)

TAGGED_CHOICES = (
    ('all', _('All')),
    ('false', _('Untagged Votes')),
)

ORDER_CHOICES = (
    ('time', _('Time')),
    ('controversy', _('Controversy')),
    ('against-party', _('Against Party')),
    ('votes', _('Number of votes')),
)

BILL_STAGE_CHOICES = (
        (u'?', _(u'Unknown')),
        (u'0', _(u'Frozen in previous knesset')),
        (u'1', _(u'Proposed')),
        (u'2', _(u'Pre-Approved')),
        (u'-2',_(u'Failed Pre-Approval')),
        (u'-2.1', _(u'Converted to discussion')),
        (u'3', _(u'In Committee')),
        (u'4', _(u'First Vote')),
        (u'-4',_(u'Failed First Vote')),
        (u'5', _(u'Committee Corrections')),
        (u'6', _(u'Approved')),
        (u'-6',_(u'Failed Approval')),
)

BILL_AGRR_STAGES = { 'proposed':Q(stage__isnull=False),
                'pre':Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6'),
                'first':Q(stage='4')|Q(stage='5')|Q(stage='6'),
                'approved':Q(stage='6'),
              }

BILL_TAGGED_CHOICES = (
    ('all', _('All')),
    ('false', _('Untagged Proposals')),
)

