from django.db import models
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext_lazy as _
import datetime
import random
import re
import logging
import sys,traceback

SHA1_RE = re.compile('^[a-f0-9]{40}$')
alphabet = 'abcdef1234567890'

logger = logging.getLogger("open-knesset.accounts")

class EmailValidationManager(models.Manager):

    @classmethod
    def create(self,user):
        ev = EmailValidation()
        ev.user = user
        ev.email = user.email
        ev.date_requested = datetime.datetime.now()
        ev.activation_key = ''.join([random.sample(alphabet,1)[0] for x in range(40)])
        ev.save()
        logger.debug("activation key = %s", ev.activation_key)
        return ev


class EmailValidation(models.Model):
    user = models.ForeignKey(User)
    email = models.CharField(max_length=50)
    date_requested = models.DateField()
    activation_key = models.CharField(_('activation key'), max_length=40)

    def __unicode__(self):
        return u'%s at %s' % (str(self.user),str(self.date_requested))

    objects = EmailValidationManager()

    @classmethod
    def validate(self, user, key):
        if not SHA1_RE.search(key):
            return (False, _("%(key)s does not look like an activation key.") % {'key': key})
        try:
            ev = self.objects.get(activation_key=key)
            if user.email != ev.email:
                return (False, _("The user has updated the email since this activation key was sent."))
            if ev.date_requested+datetime.timedelta(days=3) < datetime.date.today():
                return (False, _("This activation key has expired."))
            # email validation successful
            p = Permission.objects.get(name='Can add comment')
            ev.user.user_permissions.add(p)
            ev.user.save()
            ev.activation_key = ''
            ev.save()
            return (True, "")
        except self.DoesNotExist:
            return (False, _("Invalid activation key."))
        except Exception, e:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            logger.error("%s", ''.join(traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)))
            return (False, "Something went wrong.")
    
