#encoding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from actstream import follow
from actstream.models import Follow

from knesset.mks.models import Party, Member

class UserProfile(models.Model):
    ''' 
    This model is extending the builtin user model.  
    The extension includes a list of followed parties and members.

    >>> daonb = User.objects.create(username='daonb')
    >>> profile = daonb.get_profile()
    >>> legalize = Party.objects.create(name='legalize')
    >>> follow(daonb, legalize)
    <Follow: daonb -> legalize>
    >>> legalize == daonb.get_profile().parties[0]
    True
    >>> dbg = Member.objects.create(name='david ben gurion')
    >>> follow(daonb, dbg)
    <Follow: daonb -> david ben gurion>
    >>> dbg == daonb.get_profile().members[0]
    True

    '''

    user = models.ForeignKey(User, unique=True, related_name='profiles')

    @property
    def members(self):
        #TODO: ther has to be a faster way
        return map(lambda x: x.actor, 
            Follow.objects.filter(user=self.user, content_type=ContentType.objects.get_for_model(Member)))

    @property
    def parties(self):
        #TODO: ther has to be a faster way
        return map(lambda x: x.actor, 
            Follow.objects.filter(user=self.user, content_type=ContentType.objects.get_for_model(Party)))

    def get_badges(self):
        badges = self.badges.all()
        badges.sort(lambda x, y: cmp(x.__str__(), y.__str__()))
        return badges
        
    @models.permalink
    def get_absolute_url(self):
        return ('public-profile', (), {'object_id': self.user.id})

    def has(self, badge_type):
        return self.badges.filter(badge_type=badge_type).count()>0
        
def handle_user_save(sender, created, instance, **kwargs):
    if created and instance._state.db=='default':
        UserProfile.objects.create(user=instance)
post_save.connect(handle_user_save, sender=User)
