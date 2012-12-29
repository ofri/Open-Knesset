# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Helptext.moreinfo'
        db.add_column('okhelptexts_helptext', 'moreinfo', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Helptext.moreinfo'
        db.delete_column('okhelptexts_helptext', 'moreinfo')


    models = {
        'okhelptexts.helptext': {
            'Meta': {'object_name': 'Helptext'},
            'fulltext': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moreinfo': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'okhelptexts.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'helptext': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['okhelptexts.Helptext']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kw_text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['okhelptexts']
