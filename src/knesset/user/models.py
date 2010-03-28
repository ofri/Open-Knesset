#encoding: utf-8
from django.db import models
from knesset.mksi.models import Party, Member
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.ForeignKey('User')
    followed_parties = models.ManyToManyField(Party, related_name='followed_by')
    followed_members = models.ManyToManyField(Member, related_name='followed_by')
