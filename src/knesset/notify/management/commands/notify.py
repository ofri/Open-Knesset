from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User,Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.utils import translation
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.conf import settings
import datetime
from optparse import make_option
import logging
logger = logging.getLogger("open-knesset.notify") 

from actstream.models import Follow, Action
from mailer import send_html_mail
from knesset.mks.models import Member
from knesset.laws.models import Bill
from knesset.agendas.models import Agenda
from knesset.notify.models import LastSent
from knesset.user.models import UserProfile

class Command(NoArgsCommand):
    help = "Send e-mail notification to users that requested it."

    requires_model_validation = False

    update_models = [Member,Bill,Agenda,None]
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'email@example.com')
    days_back = getattr(settings, 'DEFAULT_NOTIFICATION_DAYS_BACK', 10)
    print days_back
    lang = getattr(settings, 'LANGUAGE_CODE', 'he')
    domain = Site.objects.get_current().domain

    option_list = NoArgsCommand.option_list + (
        make_option('--daily', action='store_true', dest='daily',
            help="send notifications to users that requested a daily update"),
        make_option('--weekly', action='store_true', dest='weekly',
            help="send notifications to users that requested a weekly update"))
            
    
    @classmethod
    def get_model_headers(cls, model):
        ''' for a given model this function returns a tuple with 
            (model, text_header, html_header)
        '''
        try:
            template_name = 'notify/%s_section' % model.__name__.lower()
            return (model, render_to_string(template_name + '.txt'), render_to_string(template_name + '.html')) 
        except TemplateDoesNotExist:
            return (model, model._meta.verbose_name_plural, '<h2>%s</h2>' % model._meta.verbose_name_plural.format()) 
        except AttributeError:
            return (model, _('Other Updates'), '<h2>%s</h2>' % _('Other Updates')) 

    def get_email_for_user(self, user):
        print user.username
        updates = dict(zip(self.update_models, ([] for x in self.update_models))) # will contain the updates to be sent
        updates_html = dict(zip(self.update_models, ([] for x in self.update_models)))
        follows = Follow.objects.filter(user=user) # everything this user is following
        # sometime a user follows something several times. we want to filter that out:
        follows = set([f.actor for f in follows])
        for f in follows:
            
            if not f:
                logger.warning('Follow object with None actor. ignoring')
                continue
            print "object = %s    id = %d" % (f, f.id)
            model_class = f.__class__
            model_template = f.__class__.__name__.lower()
            try: 
                model_name = f.__class__._meta.verbose_name
            except AttributeError:
                logger.warning('follows %d has no __class__?' % f.id)
                model_name = ""
            content_type = ContentType.objects.get_for_model(f)
            if model_class in updates:
                key = model_class
            else:
                key = None # put all updates for 'other' classes at the 'None' group
            try: # get actions that happened since last update
                last_sent = LastSent.objects.get(user=user, content_type=content_type, object_pk=f.id)
                last_sent_time = last_sent.time
                print "last_sent_time = %s" % str(last_sent_time)
                stream = Action.objects.filter(actor_content_type = content_type,
                                               actor_object_id = f.id,
                                               timestamp__gt=last_sent_time,
                                               ).order_by('-timestamp')
                last_sent.save() # update timestamp
            except LastSent.DoesNotExist: # never updates about this actor, send some updates 
                stream = Action.objects.filter(actor_content_type = content_type,
                                               actor_object_id = f.id,
                                               timestamp__gt=datetime.datetime.now()-datetime.timedelta(self.days_back),
                                               ).order_by('-timestamp')
                last_sent = LastSent.objects.create(user=user,content_type=content_type, object_pk=f.id)
                print "first time sending this object"
            if stream: # this actor has some updates
                print("len(stream)=%d" % len(stream))
                try: # genereate the appropriate header for this actor class
                    header = render_to_string(('notify/%(model)s_header.txt' % {'model': model_template}),{'model':model_name,'object':f})
                except TemplateDoesNotExist:
                    header = render_to_string(('notify/model_header.txt'),{'model':model_name,'object':f})
                try:
                    header_html = render_to_string(('notify/%(model)s_header.html' % {'model': model_template}),{'model':model_name,'object':f,'domain':self.domain})
                except TemplateDoesNotExist:                            
                    header_html = render_to_string(('notify/model_header.html'),{'model':model_name,'object':f,'domain':self.domain})
                updates[key].append(header)
                updates_html[key].append(header_html)
                
            for action_instance in stream: # now generate the updates themselves
                print "action_instance = %s" % action_instance
                try:                            
                    action_output = render_to_string(('activity/%(verb)s/action_email.txt' % { 'verb':action_instance.verb.replace(' ','_') }),{ 'action':action_instance },None)
                except TemplateDoesNotExist: # fallback to the generic template
                    action_output = render_to_string(('activity/action_email.txt'),{ 'action':action_instance },None)
                try:
                    action_output_html = render_to_string(('activity/%(verb)s/action_email.html' % { 'verb':action_instance.verb.replace(' ','_') }),{ 'action':action_instance,'domain':self.domain },None)
                except TemplateDoesNotExist: # fallback to the generic template
                    action_output_html = render_to_string(('activity/action_email.html'),{ 'action':action_instance,'domain':self.domain },None)
                updates[key].append(action_output)
                updates_html[key].append(action_output_html)
                
        email_body = []
        email_body_html = []
        for (model_class,title,title_html) in map(self.get_model_headers, self.update_models):
            if updates[model_class]: # this model has some updates, add it to the email
                email_body.append(title.format())
                email_body.append('\n'.join(updates[model_class]))
                email_body_html.append(title_html.format())
                email_body_html.append(''.join(updates_html[model_class]))
        return (email_body, email_body_html)


    def handle_noargs(self, **options):
        
        daily = options.get('daily', False)
        weekly = options.get('weekly', False)
        if not daily and not weekly:
            print "use --daily or --weekly"
            return
        
        translation.activate(self.lang)
        
        email_notification = []
        if daily:
            email_notification.append('D')
        if weekly:
            email_notification.append('W')
        
        queued = 0
        g = Group.objects.get(name='Valid Email')
        for user in User.objects.all():
            try:
                user_profile = user.get_profile()
            except UserProfile.DoesNotExist:
                logger.warn('user %s has no userprofile' % user.username)
                continue

            if user_profile and user_profile.email_notification in email_notification and g in user.groups.all():
                # if this user has a profile (should always be true)
                # requested emails in the frequency we are handling now
                # and has validated his email
                email_body, email_body_html = self.get_email_for_user(user)
                if email_body: # there are some updates. generate email
                    header = render_to_string(('notify/header.txt'),{ 'user':user })
                    footer = render_to_string(('notify/footer.txt'),{ 'user':user,'domain':self.domain })
                    header_html = render_to_string(('notify/header.html'),{ 'user':user })
                    footer_html = render_to_string(('notify/footer.html'),{ 'user':user,'domain':self.domain })
                    send_html_mail(_('Open Knesset Updates'), "%s\n%s\n%s" % (header, '\n'.join(email_body), footer), 
                                                              "%s\n%s\n%s" % (header_html, ''.join(email_body_html), footer_html),
                                                              self.from_email,
                                                              [user.email],
                                                              )
                    queued += 1
                
        print "%d email notifications queued for sending" % queued
        
        translation.deactivate()