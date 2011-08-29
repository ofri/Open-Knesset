from django.db import models
from django.contrib.auth.models import User
from knesset.events.models import Event
from knesset.links.models import Link
from django.contrib.contenttypes import generic

class Topic(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(null=True,blank=True)
    creator = models.ForeignKey(User, related_name='agenda_items')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    events = generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk")
    links = generic.GenericRelation(Link, content_type_field="content_type",
       object_id_field="object_pk")

    @models.permalink
    def get_absolute_url(self):
        return ('topic-detail', [str(self.id)])

    def __unicode__(self):
        return "%s" % self.title
