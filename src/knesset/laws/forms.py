from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from datetime import date
from tagging.models import Tag
from models import Vote, Bill, BILL_STAGE_CHOICES, BILL_AGRR_STAGES, KnessetProposal

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

BILL_TAGGED_CHOICES = (
    ('all', _('All')),
    ('false', _('Untagged Proposals')),
)

ORDER_CHOICES = (
    ('time', _('Time')),
    ('controversy', _('Controversy')),
    ('against-party', _('Against Party')),
    ('votes', _('Number of votes')),
)

STAGE_CHOICES = (
    ('all', _('All')),
)

class VoteSelectForm(forms.Form):
    """Votes filtering form"""

    vtype = forms.ChoiceField(label=_('Vote types'), choices=TYPE_CHOICES,
            required=False, initial='all')
    tagged = forms.ChoiceField(label=_('Tags'), choices=TAGGED_CHOICES,
            required=False, initial='all')
    order = forms.ChoiceField(label=_('Order by'), choices=ORDER_CHOICES,
            required=False, initial='time')
    from_date = forms.DateField(label=_('From date'), required=False)
    to_date = forms.DateField(label=_('To date'), required=False,
            initial=date.today)

    def __init__(self, *args, **kwargs):
        super(VoteSelectForm, self).__init__(*args, **kwargs)

        tags = Tag.objects.usage_for_model(Vote)
        new_choices = list(TAGGED_CHOICES)
        new_choices.extend([(t.name, t.name) for t in tags])
        self.fields['tagged'].choices = new_choices


class BillSelectForm(forms.Form):
    """Bill filtering form"""

    stage = forms.ChoiceField(label=_('Bill Stage'), choices=BILL_STAGE_CHOICES,
            required=False, initial='all')
    tagged = forms.ChoiceField(label=_('Tags'), choices=BILL_TAGGED_CHOICES,
            required=False, initial='all')

    # TODO: add more filter options:
    # order = forms.ChoiceField(label=_('Order by'), choices=ORDER_CHOICES,
    #         required=False, initial='time')
    # from_date = forms.DateField(label=_('From date'), required=False)
    # to_date = forms.DateField(label=_('To date'), required=False,
    #         initial=date.today)

    def __init__(self, *args, **kwargs):
        super(BillSelectForm, self).__init__(*args, **kwargs)

        tags = Tag.objects.usage_for_model(Bill)
        new_choices = list(BILL_TAGGED_CHOICES)
        new_choices.extend([(t.name, t.name) for t in tags])
        self.fields['tagged'].choices = new_choices

        new_stages = list(STAGE_CHOICES)
        new_stages.extend(BILL_STAGE_CHOICES)       
        self.fields['stage'].choices = new_stages

    def clean(self):
        super(BillSelectForm, self).clean()

        #override stage error on aggregate stages (when accessing from mk page)
        if (self.data.get('stage') in BILL_AGRR_STAGES) and ('stage' in self._errors):
            del self._errors['stage']
            self.cleaned_data['stage']=self.data.get('stage')

        #clean booklet input
        booklet = self.data.get('booklet')
        if booklet:
            try:
                int(booklet)
            except ValueError:
                raise forms.ValidationError(_('Invalid booklet number'))
                self.cleaned_data['booklet']=''
            else: 
                if not (KnessetProposal.objects.filter(booklet_number=booklet).exists()):
                    raise forms.ValidationError(_('Booklet does not exist'))
                    self.cleaned_data['booklet']=''                
            
                else:
                    self.cleaned_data['booklet']=booklet

        return self.cleaned_data

