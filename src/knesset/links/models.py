from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from managers import LinksManager


class LinkType(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('title'))
    image = models.ImageField(upload_to='icons')

    def __unicode__(self):
        return self.title

class Link(models.Model):
    url = models.URLField(verbose_name='URL')
    title = models.CharField(max_length=200, verbose_name=_('title'))
    content_type   = models.ForeignKey(ContentType,
            verbose_name=_('content type'),
            related_name="content_type_set_for_%(class)s")
    object_pk      = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    link_type = models.ForeignKey(LinkType, null=True, blank=True)

    objects = LinksManager()

    class Meta:
        verbose_name = _('link')
        verbose_name_plural = _('links')

    def __unicode__(self):
        return "%s: %s" % (self.title, self.url)

