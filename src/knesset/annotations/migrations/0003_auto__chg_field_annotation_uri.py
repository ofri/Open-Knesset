# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Annotation.uri'
        db.alter_column('annotations_annotation', 'uri', self.gf('django.db.models.fields.URLField')(max_length=200))


    def backwards(self, orm):
        
        # Changing field 'Annotation.uri'
        db.alter_column('annotations_annotation', 'uri', self.gf('django.db.models.fields.CharField')(max_length=2000))


    models = {
        'annotations.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'account_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'annotator_schema_version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['annotations.AnnotationPermissions']"}),
            'quote': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'ranges': ('knesset.annotations.models.JsonField', [], {'default': '[]'}),
            'tags': ('knesset.annotations.models.JsonField', [], {'default': '[]'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user': ('knesset.annotations.models.JsonField', [], {'default': '{}'})
        },
        'annotations.annotationpermissions': {
            'Meta': {'object_name': 'AnnotationPermissions'},
            'admin': ('knesset.annotations.models.JsonField', [], {'default': '[]'}),
            'delete': ('knesset.annotations.models.JsonField', [], {'default': '[]'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read': ('knesset.annotations.models.JsonField', [], {'default': '[]'}),
            'update': ('knesset.annotations.models.JsonField', [], {'default': '[]'})
        }
    }

    complete_apps = ['annotations']
