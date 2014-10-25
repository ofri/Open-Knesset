# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Badge', fields ['profile', 'badge_type']
        db.delete_unique(u'badges_badge', ['profile_id', 'badge_type_id'])

        # Deleting model 'BadgeType'
        db.delete_table(u'badges_badgetype')

        # Deleting model 'Badge'
        db.delete_table(u'badges_badge')

        from django.contrib.contenttypes.models import ContentType
        ContentType.objects.filter(app_label='customers').delete()


    def backwards(self, orm):
        # Adding model 'BadgeType'
        db.create_table(u'badges_badgetype', (
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('badges', ['BadgeType'])

        # Adding model 'Badge'
        db.create_table(u'badges_badge', (
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='badges', to=orm['user.UserProfile'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('badge_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='badges', to=orm['badges.BadgeType'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('badges', ['Badge'])

        # Adding unique constraint on 'Badge', fields ['profile', 'badge_type']
        db.create_unique(u'badges_badge', ['profile_id', 'badge_type_id'])


    models = {

    }

    complete_apps = ['badges']
