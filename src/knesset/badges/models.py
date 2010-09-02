from datetime import datetime

from django.db import models
from django.utils.translation import ugettext as _

from knesset.user.models import UserProfile

class BadgeType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    @models.permalink
    def get_absolute_url(self):
        return ('badge-detail', (), {'object_id': self.id})
  
    def __unicode__(self):
        return _(self.name)
  
class Badge(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='badges')
    created = models.DateTimeField(default=datetime.now)
    badge_type = models.ForeignKey(BadgeType, related_name='badges')
    
    @models.permalink
    def get_absolute_url(self):
        return ('badge-detail', (), {'object_id': self.badge_type.id})
    
    def __unicode__(self):
        return self.badge_type.__unicode__()
    
    class Meta:
        unique_together=('profile','badge_type')
        ordering = ('profile', 'badge_type')
