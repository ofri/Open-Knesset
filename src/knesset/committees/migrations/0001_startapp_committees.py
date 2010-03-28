
from south.db import db
from django.db import models
from knesset.committees.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CommitteeMeeting'
        db.create_table('committees_committeemeeting', (
            ('id', orm['committees.CommitteeMeeting:id']),
            ('committee', orm['committees.CommitteeMeeting:committee']),
            ('date_string', orm['committees.CommitteeMeeting:date_string']),
            ('date', orm['committees.CommitteeMeeting:date']),
            ('protocol_text', orm['committees.CommitteeMeeting:protocol_text']),
            ('topics', orm['committees.CommitteeMeeting:topics']),
        ))
        db.send_create_signal('committees', ['CommitteeMeeting'])
        
        # Adding model 'Committee'
        db.create_table('committees_committee', (
            ('id', orm['committees.Committee:id']),
            ('name', orm['committees.Committee:name']),
        ))
        db.send_create_signal('committees', ['Committee'])
        
        # Adding ManyToManyField 'CommitteeMeeting.mks_attended'
        db.create_table('committees_committeemeeting_mks_attended', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('committeemeeting', models.ForeignKey(orm.CommitteeMeeting, null=False)),
            ('member', models.ForeignKey(orm['mks.Member'], null=False))
        ))
        
        # Adding ManyToManyField 'Committee.members'
        db.create_table('committees_committee_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('committee', models.ForeignKey(orm.Committee, null=False)),
            ('member', models.ForeignKey(orm['mks.Member'], null=False))
        ))
        
        # Adding ManyToManyField 'CommitteeMeeting.votes_mentioned'
        db.create_table('committees_committeemeeting_votes_mentioned', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('committeemeeting', models.ForeignKey(orm.CommitteeMeeting, null=False)),
            ('vote', models.ForeignKey(orm['laws.Vote'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'CommitteeMeeting'
        db.delete_table('committees_committeemeeting')
        
        # Deleting model 'Committee'
        db.delete_table('committees_committee')
        
        # Dropping ManyToManyField 'CommitteeMeeting.mks_attended'
        db.delete_table('committees_committeemeeting_mks_attended')
        
        # Dropping ManyToManyField 'Committee.members'
        db.delete_table('committees_committee_members')
        
        # Dropping ManyToManyField 'CommitteeMeeting.votes_mentioned'
        db.delete_table('committees_committeemeeting_votes_mentioned')
        
    
    
    models = {
        'committees.committee': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mks.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'committees.committeemeeting': {
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['committees.Committee']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'date_string': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mks_attended': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mks.Member']"}),
            'protocol_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'votes_mentioned': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['laws.Vote']"})
        },
        'laws.vote': {
            'against_party': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'controversy': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'full_text_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.FloatField', [], {}),
            'meeting_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'src_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'src_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'time_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'vote_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mks.Member']", 'blank': 'True'}),
            'votes_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
    
    complete_apps = ['committees']
