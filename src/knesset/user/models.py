#encoding: utf-8
from django.db import models
from knesset.mks.models import Party, Member
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ''' 
    This model is extending the builtin user model.  
    The extension includes a list of followed parties and members.

    >>> user = User.objects.create(username='daonb')
    >>> profile = user.get_profile()
    >>> legalize = Party.objects.create(name='legalize')
    >>> profile.followed_parties.add(legalize)
    >>> legalize == user.get_profile().parties[0]
    True
    >>> dbg = Member.objects.create(name='david ben gurion')
    >>> profile.followed_members.add(dbg)
    >>> dbg = user.get_profile().members[0]

    '''

    user = models.ForeignKey(User, unique=True)
    followed_parties = models.ManyToManyField(Party, related_name='followers')
    followed_members = models.ManyToManyField(Member, related_name='followers')

    @property
    def members(self):
        return self.followed_members.all()

    @property
    def parties(self):
        return self.followed_parties.all()

def handle_user_save(sender, created, instance, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(handle_user_save, sender=User)
