#encoding: utf-8
from django.db import models
from knesset.mksi.models import Party, Member
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.ForeignKey('User')
    parties = models.ManyToManyField(Party, related_name='all_members', through='Membership')
    members = models.ManyToManyField(Member, related_name='all_members', through='Membership')
