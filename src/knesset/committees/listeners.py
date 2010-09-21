from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from planet.models import Feed, Post
from actstream import action, follow
from actstream.models import Action
from annotatetext.models import Annotation
from knesset.utils import disable_for_loaddata
from knesset.mks.models import Member
from models import CommitteeMeeting

@disable_for_loaddata
def handle_cm_save(sender, created, instance, **kwargs):
    cmct = ContentType.objects.get(app_label="committees", model="committeemeeting")
    mct = ContentType.objects.get(app_label="mks", model="member")
    for m in instance.mks_attended.all():
        if Action.objects.filter(actor_object_id=m.id,
                                 actor_content_type=mct, 
                                 verb='attended', 
                                 target_object_id=instance.id,
                                 target_content_type=cmct).count()==0:    
            action.send(m, verb='attended', target=instance, description='committee meeting', timestamp=instance.date)
    
post_save.connect(handle_cm_save, sender=CommitteeMeeting)

@disable_for_loaddata
def handle_annotation_save(sender, created, instance, **kwargs):
    if created:
        action.send(instance.content_object.meeting.committee, verb='annotated',
                    target=instance, description=unicode(instance.flag_value))
        action.send(instance.user, verb='annotated',
                    target=instance, description=unicode(instance.flag_value))
        follow(instance.user, instance.content_object.meeting)
post_save.connect(handle_annotation_save, sender=Annotation)

