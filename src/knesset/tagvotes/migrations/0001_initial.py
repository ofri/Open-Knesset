
from south.db import db
from django.db import models
from knesset.tagvotes.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'TagVote'
        db.create_table('tagvotes_tagvote', (
            ('id', orm['tagvotes.TagVote:id']),
            ('tagged_item', orm['tagvotes.TagVote:tagged_item']),
            ('user', orm['tagvotes.TagVote:user']),
            ('vote', orm['tagvotes.TagVote:vote']),
        ))
        db.send_create_signal('tagvotes', ['TagVote'])
        
        # Creating unique_together for [tagged_item, user] on TagVote.
        db.create_unique('tagvotes_tagvote', ['tagged_item_id', 'user_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [tagged_item, user] on TagVote.
        db.delete_unique('tagvotes_tagvote', ['tagged_item_id', 'user_id'])
        
        # Deleting model 'TagVote'
        db.delete_table('tagvotes_tagvote')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tagging.tag': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'tagging.taggeditem': {
            'Meta': {'unique_together': "(('tag', 'content_type', 'object_id'),)"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['tagging.Tag']"})
        },
        'tagvotes.tagvote': {
            'Meta': {'unique_together': "(('tagged_item', 'user'),)"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tagged_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['tagging.TaggedItem']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tagvotes'", 'to': "orm['auth.User']"}),
            'vote': ('django.db.models.fields.IntegerField', [], {})
        }
    }
    
    complete_apps = ['tagvotes']
