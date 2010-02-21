
from south.db import db
from django.db import models
from knesset.laws.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'VoteAction'
        db.create_table('laws_voteaction', (
            ('id', orm['laws.VoteAction:id']),
            ('type', orm['laws.VoteAction:type']),
            ('member', orm['laws.VoteAction:member']),
            ('vote', orm['laws.VoteAction:vote']),
            ('against_party', orm['laws.VoteAction:against_party']),
            ('against_coalition', orm['laws.VoteAction:against_coalition']),
            ('against_opposition', orm['laws.VoteAction:against_opposition']),
        ))
        db.send_create_signal('laws', ['VoteAction'])
        
        # Adding model 'PartyVotingStatistics'
        db.create_table('laws_partyvotingstatistics', (
            ('id', orm['laws.PartyVotingStatistics:id']),
            ('party', orm['laws.PartyVotingStatistics:party']),
        ))
        db.send_create_signal('laws', ['PartyVotingStatistics'])
        
        # Adding model 'Vote'
        db.create_table('laws_vote', (
            ('id', orm['laws.Vote:id']),
            ('meeting_number', orm['laws.Vote:meeting_number']),
            ('vote_number', orm['laws.Vote:vote_number']),
            ('src_id', orm['laws.Vote:src_id']),
            ('src_url', orm['laws.Vote:src_url']),
            ('title', orm['laws.Vote:title']),
            ('time', orm['laws.Vote:time']),
            ('time_string', orm['laws.Vote:time_string']),
            ('importance', orm['laws.Vote:importance']),
            ('summary', orm['laws.Vote:summary']),
            ('full_text', orm['laws.Vote:full_text']),
            ('full_text_url', orm['laws.Vote:full_text_url']),
        ))
        db.send_create_signal('laws', ['Vote'])
        
        # Adding model 'MemberVotingStatistics'
        db.create_table('laws_membervotingstatistics', (
            ('id', orm['laws.MemberVotingStatistics:id']),
            ('member', orm['laws.MemberVotingStatistics:member']),
        ))
        db.send_create_signal('laws', ['MemberVotingStatistics'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'VoteAction'
        db.delete_table('laws_voteaction')
        
        # Deleting model 'PartyVotingStatistics'
        db.delete_table('laws_partyvotingstatistics')
        
        # Deleting model 'Vote'
        db.delete_table('laws_vote')
        
        # Deleting model 'MemberVotingStatistics'
        db.delete_table('laws_membervotingstatistics')
        
    
    
    models = {
        'laws.membervotingstatistics': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'voting_statistics'", 'unique': 'True', 'to': "orm['mks.Member']"})
        },
        'laws.partyvotingstatistics': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'voting_statistics'", 'unique': 'True', 'to': "orm['mks.Party']"})
        },
        'laws.vote': {
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
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mks.Member']", 'blank': 'True'})
        },
        'laws.voteaction': {
            'against_coalition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'against_opposition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'against_party': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'vote': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['laws.Vote']"})
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
    
    complete_apps = ['laws']
