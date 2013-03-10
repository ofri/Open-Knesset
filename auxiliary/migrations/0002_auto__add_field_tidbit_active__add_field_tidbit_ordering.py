# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tidbit.active'
        db.add_column('auxiliary_tidbit', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Tidbit.ordering'
        db.add_column('auxiliary_tidbit', 'ordering',
                      self.gf('django.db.models.fields.IntegerField')(default=20, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Tidbit.active'
        db.delete_column('auxiliary_tidbit', 'active')

        # Deleting field 'Tidbit.ordering'
        db.delete_column('auxiliary_tidbit', 'ordering')


    models = {
        'auxiliary.tidbit': {
            'Meta': {'object_name': 'Tidbit'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'button_link': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'button_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '20', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Did you know ?'", 'max_length': '40'})
        }
    }

    complete_apps = ['auxiliary']