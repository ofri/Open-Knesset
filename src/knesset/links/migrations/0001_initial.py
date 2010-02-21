
from south.db import db
from django.db import models
from knesset.links.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Link'
        db.create_table('links_link', (
            ('id', orm['links.Link:id']),
            ('url', orm['links.Link:url']),
            ('title', orm['links.Link:title']),
            ('content_type', orm['links.Link:content_type']),
            ('object_pk', orm['links.Link:object_pk']),
        ))
        db.send_create_signal('links', ['Link'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Link'
        db.delete_table('links_link')
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'links.link': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_link'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['links']
