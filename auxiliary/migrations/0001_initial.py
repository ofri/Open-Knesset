# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tidbit'
        db.create_table('auxiliary_tidbit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Did you know', max_length=40)),
            ('icon', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('button_text', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('button_link', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('auxiliary', ['Tidbit'])


    def backwards(self, orm):
        # Deleting model 'Tidbit'
        db.delete_table('auxiliary_tidbit')


    models = {
        'auxiliary.tidbit': {
            'Meta': {'object_name': 'Tidbit'},
            'button_link': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'button_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Did you know'", 'max_length': '40'})
        }
    }

    complete_apps = ['auxiliary']