from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag,TaggedItem

class TagVote(models.Model):
    """
    Holds the data for user's vote on a tag.
    """
    tagged_item     = models.ForeignKey(TaggedItem, verbose_name=_('tagged item'), related_name='votes')
    user            = models.ForeignKey(User, verbose_name=_('user'), related_name='tagvotes')
    vote            = models.IntegerField()

    class Meta:
        # Enforce unique vote per user and tagged item
        unique_together = (('tagged_item', 'user'),)
        verbose_name = _('tag vote')
        verbose_name_plural = _('tag votes')

    def __unicode__(self):
        return u'%s - %s [%d]' % (self.user, self.tagged_item, self.vote)

    def get_absolute_url(self):
        # if you try moving this line to the top you'll get bitten the cyclic
        # import monster. be warned!!!!
        from knesset.laws.models import Vote
        if self.tagged_item.content_type == ContentType.objects.get_for_model(Vote):
            return reverse('vote-tag',
                           kwargs={'tag':self.tagged_item.tag.name})
        else:
            return reverse('bill-tag',
                           kwargs={'tag':self.tagged_item.tag.name})
