# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Helptext'
        db.create_table('okhelptexts_helptext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fulltext', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('okhelptexts', ['Helptext'])

        # Adding model 'Keyword'
        db.create_table('okhelptexts_keyword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('helptext', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['okhelptexts.Helptext'])),
            ('kw_text', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('okhelptexts', ['Keyword'])


    def backwards(self, orm):
        
        # Deleting model 'Helptext'
        db.delete_table('okhelptexts_helptext')

        # Deleting model 'Keyword'
        db.delete_table('okhelptexts_keyword')


    models = {
        'okhelptexts.helptext': {
            'Meta': {'object_name': 'Helptext'},
            'fulltext': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'okhelptexts.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'helptext': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['okhelptexts.Helptext']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kw_text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['okhelptexts']
