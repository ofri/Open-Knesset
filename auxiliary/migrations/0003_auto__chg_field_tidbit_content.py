# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Tidbit.content'
        db.alter_column('auxiliary_tidbit', 'content', self.gf('tinymce.models.HTMLField')())

    def backwards(self, orm):

        # Changing field 'Tidbit.content'
        db.alter_column('auxiliary_tidbit', 'content', self.gf('django.db.models.fields.TextField')())

    models = {
        'auxiliary.tidbit': {
            'Meta': {'object_name': 'Tidbit'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'button_link': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'button_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content': ('tinymce.models.HTMLField', [], {}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '20', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Did you know ?'", 'max_length': '40'})
        }
    }

    complete_apps = ['auxiliary']