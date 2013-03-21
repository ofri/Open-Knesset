# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Suggestion.suggested_type'
        db.delete_column('suggestions_suggestion', 'suggested_type_id')

        # Deleting field 'Suggestion.subject_ct'
        db.delete_column('suggestions_suggestion', 'subject_ct_id')

        # Deleting field 'Suggestion.suggested_id'
        db.delete_column('suggestions_suggestion', 'suggested_id')

        # Deleting field 'Suggestion.field'
        db.delete_column('suggestions_suggestion', 'field')

        # Deleting field 'Suggestion.subject_id'
        db.delete_column('suggestions_suggestion', 'subject_id')


    def backwards(self, orm):
        # Adding field 'Suggestion.suggested_type'
        db.add_column('suggestions_suggestion', 'suggested_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='suggested_content', null=True, to=orm['contenttypes.ContentType'], blank=True),
                      keep_default=False)

        # Adding field 'Suggestion.subject_ct'
        db.add_column('suggestions_suggestion', 'subject_ct',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='suggestion_subject', null=True, to=orm['contenttypes.ContentType'], blank=True),
                      keep_default=False)

        # Adding field 'Suggestion.suggested_id'
        db.add_column('suggestions_suggestion', 'suggested_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Suggestion.field'
        db.add_column('suggestions_suggestion', 'field',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Suggestion.subject_id'
        db.add_column('suggestions_suggestion', 'subject_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'suggestions.suggestion': {
            'Meta': {'object_name': 'Suggestion'},
            'action': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resolved_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'resolved_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'resolved_suggestions'", 'null': 'True', 'to': "orm['auth.User']"}),
            'resolved_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'suggested_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'suggested_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suggestions'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['suggestions']