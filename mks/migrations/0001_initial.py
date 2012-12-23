#encoding: utf-8

from south.db import db
from django.db import models
from mks.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Party'
        db.create_table('mks_party', (
            ('id', orm['mks.Party:id']),
            ('name', orm['mks.Party:name']),
            ('start_date', orm['mks.Party:start_date']),
            ('end_date', orm['mks.Party:end_date']),
            ('is_coalition', orm['mks.Party:is_coalition']),
            ('number_of_members', orm['mks.Party:number_of_members']),
            ('number_of_seats', orm['mks.Party:number_of_seats']),
        ))
        db.send_create_signal('mks', ['Party'])
        
        # Adding model 'Membership'
        db.create_table('mks_membership', (
            ('id', orm['mks.Membership:id']),
            ('member', orm['mks.Membership:member']),
            ('party', orm['mks.Membership:party']),
            ('start_date', orm['mks.Membership:start_date']),
            ('end_date', orm['mks.Membership:end_date']),
        ))
        db.send_create_signal('mks', ['Membership'])
        
        # Adding model 'Correlation'
        db.create_table('mks_correlation', (
            ('id', orm['mks.Correlation:id']),
            ('m1', orm['mks.Correlation:m1']),
            ('m2', orm['mks.Correlation:m2']),
            ('score', orm['mks.Correlation:score']),
            ('normalized_score', orm['mks.Correlation:normalized_score']),
            ('not_same_party', orm['mks.Correlation:not_same_party']),
        ))
        db.send_create_signal('mks', ['Correlation'])
        
        # Adding model 'Member'
        db.create_table('mks_member', (
            ('id', orm['mks.Member:id']),
            ('name', orm['mks.Member:name']),
            ('current_party', orm['mks.Member:current_party']),
            ('start_date', orm['mks.Member:start_date']),
            ('end_date', orm['mks.Member:end_date']),
            ('img_url', orm['mks.Member:img_url']),
            ('phone', orm['mks.Member:phone']),
            ('fax', orm['mks.Member:fax']),
            ('email', orm['mks.Member:email']),
            ('website', orm['mks.Member:website']),
            ('family_status', orm['mks.Member:family_status']),
            ('number_of_children', orm['mks.Member:number_of_children']),
            ('date_of_birth', orm['mks.Member:date_of_birth']),
            ('place_of_birth', orm['mks.Member:place_of_birth']),
            ('date_of_death', orm['mks.Member:date_of_death']),
            ('year_of_aliyah', orm['mks.Member:year_of_aliyah']),
            ('is_current', orm['mks.Member:is_current']),
        ))
        db.send_create_signal('mks', ['Member'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Party'
        db.delete_table('mks_party')
        
        # Deleting model 'Membership'
        db.delete_table('mks_membership')
        
        # Deleting model 'Correlation'
        db.delete_table('mks_correlation')
        
        # Deleting model 'Member'
        db.delete_table('mks_member')
        
    
    
    models = {
        'mks.correlation': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'm1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'m1'", 'to': "orm['mks.Member']"}),
            'm2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'m2'", 'to': "orm['mks.Member']"}),
            'normalized_score': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'not_same_party': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mks.member': {
            'current_party': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'members'", 'null': 'True', 'to': "orm['mks.Party']"}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'family_status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number_of_children': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parties': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mks.Party']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'place_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'year_of_aliyah': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.membership': {
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Party']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.party': {
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_coalition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number_of_members': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_seats': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['mks']
