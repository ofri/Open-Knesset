from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext

from actstream import action
from actstream.models import Follow

from knesset.user.models import UserProfile
from knesset.mks.models import Member
from knesset.badges.models import Badge, BadgeType

class BadgeHandler(object):
    def __init__(self, badge_name, badge_description):
        self.badge_name = badge_name
        self.badge_description = badge_description
    
    def __call__(self, sender, **kwargs):
        if self.test(sender, **kwargs):
            profile = self.get_profile(sender, **kwargs)
            self.create_badge(profile)  
    
    def test(self, sender, **kwargs):
        """Has user reached achivment criteria for this badge"""
        return False

    def get_profile(self, sender, **kwargs):
        """Get user profile"""
        return None
        
    def create_badge(self, profile):
        """Create badge, if not exist"""
        (badge_type, created) = BadgeType.objects.get_or_create(name=self.badge_name, description=self.badge_description)
        (badge, created) = Badge.objects.get_or_create(profile = profile, badge_type = badge_type)
        if created:
            action.send(profile.user, verb='got badge', target=badge)

class PostFollowSaveHandler(BadgeHandler):
    def get_profile(self, sender, **kwargs):
        instance = kwargs.get('instance',None)
        return instance.user.profiles.all()[0]
        
class FirstFollowHandler(PostFollowSaveHandler):
    """
    First Follow Badge is a badge you get when you follow something for the first time
    """    
    def __init__(self):
        # These two lines make sure translation identifies these strings
        name = ugettext(u'FirstFollow')
        description = ugettext(u'You are following something')
        
        super(FirstFollowHandler, self).__init__(badge_name=name, badge_description=description)
        
    def test(self, sender, **kwargs):
        return True # on each follow, this achivment is granted

def first_follow_handler(sender, **kwargs):
    FirstFollowHandler().__call__(sender, **kwargs)
post_save.connect(first_follow_handler, sender=Follow)

class FirstFollowMKHandler(FirstFollowHandler):
    """
    First Follow Badge is a badge you get when you follow an MK.
    """   
    def __init__(self):
        # These two lines make sure translation identifies these strings
        name = ugettext(u'FirstMKFollow')
        description = ugettext(u'You are following an MK')
        
        super(FirstFollowHandler, self).__init__(badge_name=name, badge_description=description)
    
    def test(self, sender, **kwargs):
        instance = kwargs.get('instance',None)
        return instance is not None and isinstance(instance.actor, Member)

def first_follow_mk_handler(sender, **kwargs):
    FirstFollowMKHandler().__call__(sender, **kwargs)
post_save.connect(first_follow_mk_handler, sender=Follow)

