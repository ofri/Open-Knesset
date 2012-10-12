from django.utils.translation import ugettext_lazy as _

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
