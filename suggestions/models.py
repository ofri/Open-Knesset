from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Suggestion(models.Model):
    """Data improvement suggestions.  Designed to implement suggestions queue
    for content editors.

    A suggestion can be either:

    * Automatically applied once approved (for that data needs to to supplied
      and action be one of: ADD, DELETE, UPDATE. If the the field to be
      modified is a relation manger, `content_object` should be provided as
      well.
    * Manually applied, in that case a content should be provided for
      `suggested_text`.

    The model is generic is possible, and designed for building custom
    suggestion forms for each content type.

    """

    ADD, DELETE, UPDATE, REPLACE, FREE_TEXT = range(5)

    SUGGEST_CHOICES = (
        (ADD, _('Add')),
        (DELETE, _('Delete')),
        (UPDATE, _('update field')),
        (REPLACE, _('Replace partial string')),
        (FREE_TEXT, _('Free textual description')),
    )

    NEW, FIXED, WONTFIX = 0, 1, 2

    RESOLVE_CHOICES = (
        (NEW, _('New')),
        (FIXED, _('Fixed')),
        (WONTFIX, _("Won't Fix")),
    )

    suggested_at = models.DateTimeField(
        _('Suggested at'), blank=True, default=datetime.now, db_index=True)
    suggested_by = models.ForeignKey(User, related_name='suggestions')

    content_type = models.ForeignKey(
        ContentType, related_name='suggestion_content')
    content_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'content_id')

    suggestion_type = models.PositiveIntegerField(
        _('Suggestion type'), choices=SUGGEST_CHOICES)

    # suggestion can be either a foreign key adding to some related manager,
    # set some content text, etc
    suggested_field = models.CharField(
        max_length=255, blank=True, null=True,
        help_text=_('Field or related manager to change'))
    suggested_type = models.ForeignKey(
        ContentType, related_name='suggested_content')
    suggested_id = models.PositiveIntegerField()
    suggested_object = generic.GenericForeignKey('content_type', 'content_id')
    suggested_text = models.TextField(_('Suggested free text'), blank=True, null=True)

    resolved_at = models.DateTimeField(
        _('resolved at'), blank=True, default=datetime.now)
    resolved_by = models.ForeignKey(
        User, related_name='resolved_suggestions', blank=True, null=True)
    resolved_status = models.IntegerField(
        _('Resolved status'), db_index=True, default=NEW,
        choices=RESOLVE_CHOICES)

    class Meta:
        verbose_name = _('Suggestion')
        verbose_name_plural = _('Suggestions')
